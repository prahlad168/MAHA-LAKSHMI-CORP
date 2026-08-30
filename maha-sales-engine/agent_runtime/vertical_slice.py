from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

from .actions import ActionRegistry, ActionRequest, ActionResult
from .agents import Agent, AgentRegistry
from .director import Director
from .events import EventLog
from .qualification import qualify_lead
from .skills import Skill, SkillRegistry
from .store import AgentStore


class WhatsAppSender(Protocol):
    def send(self, phone: str, message: str) -> Any: ...


@dataclass
class SalesRuntime:
    """Durable Research -> Qualification -> CRM -> Sales -> Approval runtime."""

    director: Director
    events: EventLog
    actions: ActionRegistry
    agents: AgentRegistry
    skills: SkillRegistry
    store: AgentStore

    def run(self, request: str, candidates: list[dict[str, Any]]) -> Task:
        task = Task(request=request, metadata={"candidates": candidates})
        self.store.save_task(task)
        self.events.emit(task.id, "TASK_CREATED", request=request)
        research_result = self.director.run_once(task, "research", finalize=False)
        self.store.save_task(task)
        if not research_result or not research_result.success:
            return task
        sales_result = self.director.run_once(task, "sales", finalize=False)
        self.store.save_task(task)
        if not sales_result or not sales_result.success:
            return task
        task.transition(TaskStatus.WAITING)
        task.current_action = "human_approval"
        self.events.emit(task.id, "WAITING_FOR_APPROVAL", approvals=len(task.result or []))
        self.store.save_task(task)
        return task

    def approve(self, approval_id: str, reviewer: str) -> dict[str, Any]:
        self.store.review_approval(approval_id, "approved", reviewer)
        approval = self.store.get_approval(approval_id)
        if not approval:
            raise ValueError("approval not found")
        self.store.set_lead_status(approval["lead_id"], "contacted")
        self.store.set_followup_state(approval["lead_id"], "scheduled")
        self.events.emit(approval["task_id"], "APPROVAL_GRANTED", approval_id=approval_id, reviewer=reviewer)
        return approval

    def reject(self, approval_id: str, reviewer: str) -> None:
        self.store.review_approval(approval_id, "rejected", reviewer)
        approval = self.store.get_approval(approval_id)
        if approval:
            self.store.set_followup_state(approval["lead_id"], "stopped")
            self.events.emit(approval["task_id"], "APPROVAL_REJECTED", approval_id=approval_id, reviewer=reviewer)

    def send_approved(self, approval_id: str, sender: WhatsAppSender) -> Any:
        approval = self.store.get_approval(approval_id)
        if not approval or approval["status"] != "approved":
            raise ValueError("message must be approved before sending")
        phone = approval["payload"].get("phone")
        message = approval["payload"].get("message")
        if not phone or not message:
            raise ValueError("approved payload requires phone and message")
        result = sender.send(phone, message)
        self.store.mark_approval_sent(approval_id)
        self.store.set_lead_status(approval["lead_id"], "contacted")
        self.store.set_followup_state(approval["lead_id"], "sent", last_contacted_at=datetime.now(timezone.utc).isoformat())
        self.events.emit(approval["task_id"], "WHATSAPP_SENT", approval_id=approval_id, lead_id=approval["lead_id"])
        return result


def _normalize_leads(task: Task) -> list[dict[str, Any]]:
    """Normalize, deduplicate and qualify candidates."""
    output: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in task.metadata.get("candidates", []):
        company = str(raw.get("company", "")).strip()
        if not company or company.casefold() in seen:
            continue
        seen.add(company.casefold())
        lead = {
            "name": str(raw.get("name", "")).strip(), "email": str(raw.get("email", "")).strip(),
            "phone": str(raw.get("phone", "")).strip(), "whatsapp": str(raw.get("whatsapp", "")).strip(),
            "website": str(raw.get("website", "")).strip(), "company": company,
            "industry": str(raw.get("industry", "business")).strip() or "business",
            "country": str(raw.get("country", "Indonesia")).strip() or "Indonesia",
            "language": str(raw.get("language", "id")).strip() or "id",
            "source": str(raw.get("source", "research")).strip() or "research",
            "source_url": raw.get("source_url"), "researched_at": raw.get("researched_at"),
        }
        qualified = qualify_lead(lead)
        if qualified["tier"] != "reject":
            output.append(qualified)
    return sorted(output, key=lambda item: (-item["score"], item["company"]))


def _persist_leads(parameters: dict[str, Any]) -> list[dict[str, Any]]:
    store: AgentStore = parameters["store"]
    return [store.upsert_lead(lead) for lead in parameters.get("leads", [])]


def _generate_sales(parameters: dict[str, Any]) -> list[dict[str, Any]]:
    """Generate outreach copy through ContentEngine and create human approvals."""
    content_engine = parameters.get("content_engine")
    store: AgentStore = parameters["store"]
    task_id = parameters["task_id"]
    if content_engine is None:
        raise ValueError("content_engine is required for sales outreach generation")
    results = []
    for lead in parameters.get("leads", []):
        message = content_engine.generate_whatsapp_content("whatsapp_initial", lead)
        payload = {
            "lead_id": lead["id"], "company": lead["company"], "phone": lead.get("phone"),
            "channel": "whatsapp", "tier": lead["tier"], "score": lead["score"], "message": message,
        }
        approval_id = store.create_approval(task_id, lead["id"], "whatsapp", payload)
        store.set_followup_state(lead["id"], "awaiting_approval")
        results.append({**payload, "approval_id": approval_id, "status": "pending_approval"})
    return results


def build_sales_runtime(db_path: Path, content_engine: Any) -> SalesRuntime:
    store = AgentStore(db_path)
    events, actions, agents, skills = EventLog(store), ActionRegistry(), AgentRegistry(), SkillRegistry()
    skills.register(Skill("lead-generation", _normalize_leads, version="1.2.0"))

    def research_plan(task: Task) -> ActionRequest:
        skill = skills.get("lead-generation")
        assert skill is not None
        return ActionRequest("persist_leads", {"store": store, "leads": skill.run(task)})

    def sales_plan(task: Task) -> ActionRequest:
        return ActionRequest("generate_sales_outreach", {
            "leads": task.result if isinstance(task.result, list) else [],
            "content_engine": content_engine, "store": store, "task_id": task.id,
        })

    actions.register("persist_leads", _persist_leads)
    actions.register("generate_sales_outreach", _generate_sales)
    agents.register(Agent("research", research_plan))
    agents.register(Agent("sales", sales_plan))
    return SalesRuntime(Director(agents, skills, actions, events), events, actions, agents, skills, store)


def register_with_core_engine(core_engine: Any, content_engine: Any) -> SalesRuntime:
    runtime = build_sales_runtime(Path(core_engine.db.db_path), content_engine)
    core_engine.register_module("agent_runtime", runtime)
    return runtime
