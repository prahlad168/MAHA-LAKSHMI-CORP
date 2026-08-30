from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .actions import ActionRegistry, ActionRequest, ActionResult
from .agents import Agent, AgentRegistry
from .director import Director
from .events import EventLog
from .skills import Skill, SkillRegistry
from .task import Task, TaskStatus


@dataclass
class SalesRuntime:
    """Application wiring for the first Research -> Lead Gen -> Sales slice."""

    director: Director
    events: EventLog
    actions: ActionRegistry
    agents: AgentRegistry
    skills: SkillRegistry

    def run(self, request: str, candidates: list[dict[str, Any]]) -> Task:
        task = Task(request=request, metadata={"candidates": candidates})

        # Stage 1: research agent uses the lead-generation skill to normalize input.
        research_result = self.director.run_once(task, "research")
        if not research_result or not research_result.success:
            return task

        # Stage 2: sales agent consumes the normalized leads produced by research.
        task.transition(TaskStatus.PENDING)
        task.result = research_result.data
        sales_result = self.director.run_once(task, "sales")
        if not sales_result or not sales_result.success:
            return task

        task.result = sales_result.data
        task.transition(TaskStatus.COMPLETED)
        return task


def _normalize_leads(task: Task) -> list[dict[str, Any]]:
    """Lead-generation skill: normalize and conservatively score supplied candidates."""
    output: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in task.metadata.get("candidates", []):
        company = str(raw.get("company", "")).strip()
        if not company:
            continue
        key = company.casefold()
        if key in seen:
            continue
        seen.add(key)
        lead = {
            "name": str(raw.get("name", "")).strip(),
            "email": str(raw.get("email", "")).strip(),
            "phone": str(raw.get("phone", "")).strip(),
            "company": company,
            "industry": str(raw.get("industry", "business")).strip() or "business",
            "country": str(raw.get("country", "Indonesia")).strip() or "Indonesia",
            "language": str(raw.get("language", "id")).strip() or "id",
            "source": str(raw.get("source", "research")).strip() or "research",
        }
        score = 0
        score += 30 if lead["phone"] else 0
        score += 25 if lead["email"] else 0
        score += 20 if lead["industry"] in {"restaurant", "cafe", "hotel", "tour", "retail"} else 10
        score += 15 if lead["country"].casefold() == "indonesia" else 5
        lead["score"] = min(score, 100)
        output.append(lead)
    return sorted(output, key=lambda item: (-item["score"], item["company"]))


def _persist_leads(parameters: dict[str, Any]) -> list[dict[str, Any]]:
    """Persist qualified leads using the existing MAHA SQLite database."""
    import sqlite3
    from uuid import uuid4
    from datetime import datetime

    db_path = Path(parameters["db_path"])
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS leads (
                id TEXT PRIMARY KEY, name TEXT NOT NULL, email TEXT, phone TEXT,
                company TEXT, industry TEXT, country TEXT, language TEXT, source TEXT,
                status TEXT DEFAULT 'new', score INTEGER DEFAULT 0, created_at TEXT,
                last_contact TEXT, followup_count INTEGER DEFAULT 0, notes TEXT
            )"""
        )
        persisted = []
        now = datetime.now().isoformat()
        for lead in parameters.get("leads", []):
            lead_id = f"LEAD-{uuid4().hex[:12].upper()}"
            conn.execute(
                """INSERT INTO leads
                (id,name,email,phone,company,industry,country,language,source,status,score,created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (lead_id, lead["name"] or "Business Owner", lead["email"], lead["phone"],
                 lead["company"], lead["industry"], lead["country"], lead["language"],
                 lead["source"], "qualified", lead["score"], now),
            )
            persisted.append({**lead, "id": lead_id})
        conn.commit()
        return persisted
    finally:
        conn.close()


def _generate_sales(parameters: dict[str, Any]) -> list[dict[str, Any]]:
    """Generate non-sending outreach copy; delivery remains outside this slice."""
    results = []
    for lead in parameters.get("leads", []):
        first_name = lead.get("name", "").split()[0] if lead.get("name") else ""
        greeting = f"Halo {first_name}!" if first_name else "Halo!"
        message = (
            f"{greeting} Saya dari MAHA LAKSHMI. Kami membantu bisnis {lead['industry']} "
            f"seperti {lead['company']} meningkatkan lead generation melalui WhatsApp. "
            "Apakah Anda terbuka untuk melihat contoh WhatsApp Marketing Kit kami?"
        )
        results.append({"lead_id": lead["id"], "company": lead["company"], "channel": "whatsapp", "message": message})
    return results


def build_sales_runtime(db_path: Path) -> SalesRuntime:
    events = EventLog()
    actions = ActionRegistry()
    agents = AgentRegistry()
    skills = SkillRegistry()

    skills.register(Skill("lead-generation", _normalize_leads, version="1.0.0"))

    def research_plan(task: Task) -> ActionRequest:
        skill = skills.get("lead-generation")
        assert skill is not None
        leads = skill.run(task)
        return ActionRequest("persist_leads", {"db_path": str(db_path), "leads": leads})

    def sales_plan(task: Task) -> ActionRequest:
        persisted = task.result if isinstance(task.result, list) else []
        return ActionRequest("generate_sales_outreach", {"leads": persisted})

    actions.register("persist_leads", _persist_leads)
    actions.register("generate_sales_outreach", _generate_sales)
    agents.register(Agent("research", research_plan))
    agents.register(Agent("sales", sales_plan))

    return SalesRuntime(
        director=Director(agents, skills, actions, events),
        events=events,
        actions=actions,
        agents=agents,
        skills=skills,
    )
