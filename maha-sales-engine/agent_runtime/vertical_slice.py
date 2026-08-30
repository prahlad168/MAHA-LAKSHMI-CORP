from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .actions import ActionRegistry, ActionRequest, ActionResult
from .agents import Agent, AgentRegistry
from .director import Director
from .events import EventLog
from .qualification import qualify_lead
from .skills import Skill, SkillRegistry
from .task import Task, TaskStatus


@dataclass
class SalesRuntime:
    """Application wiring for Research -> Qualification -> Lead Gen -> Sales."""

    director: Director
    events: EventLog
    actions: ActionRegistry
    agents: AgentRegistry
    skills: SkillRegistry

    def run(self, request: str, candidates: list[dict[str, Any]]) -> Task:
        task = Task(request=request, metadata={"candidates": candidates})
        research_result = self.director.run_once(task, "research", finalize=False)
        if not research_result or not research_result.success:
            return task
        sales_result = self.director.run_once(task, "sales", finalize=True)
        if not sales_result or not sales_result.success:
            return task
        task.result = sales_result.data
        return task


def _normalize_leads(task: Task) -> list[dict[str, Any]]:
    """Normalize, deduplicate and qualify candidates using the transparent V1 policy."""
    output: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in task.metadata.get("candidates", []):
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
            "source": str(raw.get("source", "research")).strip() or "research",
        }
        qualified = qualify_lead(lead)
        if qualified["tier"] != "reject":
            output.append(qualified)
    return sorted(output, key=lambda item: (-item["score"], item["company"]))


def _persist_leads(parameters: dict[str, Any]) -> list[dict[str, Any]]:
    """Persist qualified leads using the existing MAHA SQLite database."""
    import sqlite3
    from datetime import datetime
    from uuid import uuid4

    db_path = Path(parameters["db_path"])
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("""CREATE TABLE IF NOT EXISTS leads (
            id TEXT PRIMARY KEY, name TEXT NOT NULL, email TEXT, phone TEXT,
            company TEXT, industry TEXT, country TEXT, language TEXT, source TEXT,
            status TEXT DEFAULT 'new', score INTEGER DEFAULT 0, created_at TEXT,
            last_contact TEXT, followup_count INTEGER DEFAULT 0, notes TEXT
        )""")
        persisted = []
        now = datetime.now().isoformat()
        for lead in parameters.get("leads", []):
            lead_id = f"LEAD-{uuid4().hex[:12].upper()}"
            conn.execute("""INSERT INTO leads
                (id,name,email,phone,company,industry,country,language,source,status,score,created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (lead_id, lead["name"] or "Business Owner", lead["email"], lead["phone"],
                 lead["company"], lead["industry"], lead["country"], lead["language"],
                 lead["source"], lead["tier"], lead["score"], now))
            persisted.append({**lead, "id": lead_id})
        conn.commit()
        return persisted
    finally:
        conn.close()


def _generate_sales(parameters: dict[str, Any]) -> list[dict[str, Any]]:
    """Generate non-sending outreach copy through the existing MAHA ContentEngine."""
    content_engine = parameters.get("content_engine")
    if content_engine is None:
        raise ValueError("content_engine is required for sales outreach generation")
    results = []
    for lead in parameters.get("leads", []):
        message = content_engine.generate_whatsapp_content("whatsapp_initial", lead)
        results.append({"lead_id": lead["id"], "company": lead["company"],
                        "tier": lead["tier"], "score": lead["score"],
                        "channel": "whatsapp", "message": message})
    return results


def build_sales_runtime(db_path: Path, content_engine: Any) -> SalesRuntime:
    events, actions, agents, skills = EventLog(), ActionRegistry(), AgentRegistry(), SkillRegistry()
    skills.register(Skill("lead-generation", _normalize_leads, version="1.1.0"))

    def research_plan(task: Task) -> ActionRequest:
        skill = skills.get("lead-generation")
        assert skill is not None
        return ActionRequest("persist_leads", {"db_path": str(db_path), "leads": skill.run(task)})

    def sales_plan(task: Task) -> ActionRequest:
        return ActionRequest("generate_sales_outreach", {
            "leads": task.result if isinstance(task.result, list) else [],
            "content_engine": content_engine,
        })

    actions.register("persist_leads", _persist_leads)
    actions.register("generate_sales_outreach", _generate_sales)
    agents.register(Agent("research", research_plan))
    agents.register(Agent("sales", sales_plan))
    return SalesRuntime(Director(agents, skills, actions, events), events, actions, agents, skills)


def register_with_core_engine(core_engine: Any, content_engine: Any) -> SalesRuntime:
    """Attach the agent runtime to the existing CoreEngine without changing its lifecycle."""
    runtime = build_sales_runtime(Path(core_engine.db.db_path), content_engine)
    core_engine.register_module("agent_runtime", runtime)
    return runtime
