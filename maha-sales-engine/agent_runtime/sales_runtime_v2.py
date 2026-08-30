from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

from .actions import ActionRegistry, ActionRequest
from .agents import Agent, AgentRegistry
from .director import Director
from .events import EventLog
from .qualification import qualify_lead
from .skills import Skill, SkillRegistry
from .store import AgentStore
from .task import Task, TaskStatus


class WhatsAppSender(Protocol):
    def send(self, phone: str, message: str) -> Any: ...


@dataclass
class SalesRuntimeV2:
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

        result = self.director.run_once(task, "research", finalize=False)
        self.store.save_task(task)
        if not result or not result.success:
            return task

        result = self.director.run_once(task, "sales", finalize=False)
        self.store.save_task(task)
        if not result or not result.success:
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
            self.store.set_lead_status(approval["lead_id"], "lost")
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
        now = datetime.now(timezone.utc).isoformat()
        self.store.mark_approval_sent(approval_id)
        self.store.set_lead_status(approval["lead_id"], "contacted")
        self.store.set_followup_state(approval["lead_id"], "sent", last_contacted_at=now)
        self.events.emit(approval["task_id"], "WHATSAPP_SENT", approval_id=approval_id, lead_id=approval["lead_id"])
        return result


def normalize_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in candidates:
        company = str(raw.get("company", "")).strip()
        if not company or company.casefold() in seen:
            continue
        seen.add(company.casefold())
        lead = {
            "name": str(raw.get("name", "")).strip(),
            "email": str(raw.get("email", "")).strip(),
            "phone": str(raw.get("phone", "")).strip(),
            "whatsapp": str(raw.get("whatsapp", "")).strip(),
            "website": str(raw.get("website", "")).strip(),
            "company": company,
            "industry": str(raw.get("industry", "business")).strip() or "business",
            "country": str(raw.get("country", "Indonesia")).strip() or "Indonesia",
            "language": str(raw.get("language", "id")).strip() or "id",
            "source": str(raw.get("source", "web_search")).strip() or "web_search",
            "source_url": raw.get("source_url"),
            "researched_at": raw.get("researched_at"),
        }
        scored = qualify_lead(lead)
        if scored["tier"] != "reject":
            output.append(scored)
    return sorted(output, key=lambda item: (-item["score"], item["company"]))


def build_sales_runtime_v2(db_path: Path, content_engine: Any) -> SalesRuntimeV2:
    store = AgentStore(db_path)
    events = EventLog(store)
    actions = ActionRegistry()
    agents = AgentRegistry()
    skills = SkillRegistry()

    skills.register(Skill("lead-generation", lambda task: normalize_candidates(task.metadata.get("candidates", [])), "1.3.0"))

    def research_plan(task: Task) -> ActionRequest:
        skill = skills.get("lead-generation")
        assert skill is not None
        leads = skill.run(task)
        return ActionRequest("persist_leads", {"leads": leads})

    def sales_plan(task: Task) -> ActionRequest:
        return ActionRequest("generate_sales_outreach", {"leads": task.result or [], "task_id": task.id})

    def persist(parameters: dict[str, Any]) -> list[dict[str, Any]]:
        return [store.upsert_lead(lead) for lead in parameters.get("leads", [])]

    def generate_outreach(parameters: dict[str, Any]) -> list[dict[str, Any]]:
        if content_engine is None:
            raise ValueError("content_engine is required")
        results = []
        for lead in parameters.get("leads", []):
            message = content_engine.generate_whatsapp_content("whatsapp_initial", lead)
            payload = {"lead_id": lead["id"], "company": lead["company"], "phone": lead.get("phone"), "channel": "whatsapp", "tier": lead["tier"], "score": lead["score"], "message": message}
            approval_id = store.create_approval(parameters["task_id"], lead["id"], "whatsapp", payload)
            store.set_followup_state(lead["id"], "awaiting_approval")
            results.append({**payload, "approval_id": approval_id, "status": "pending_approval"})
        return results

    actions.register("persist_leads", persist)
    actions.register("generate_sales_outreach", generate_outreach)
    agents.register(Agent("research", research_plan))
    agents.register(Agent("sales", sales_plan))
    return SalesRuntimeV2(Director(agents, skills, actions, events), events, actions, agents, skills, store)
