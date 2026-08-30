from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .events import TaskEvent
from .task import Task, TaskStatus


class AgentStore:
    """SQLite-backed task, event, CRM lead and approval store."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS agent_tasks (
                    id TEXT PRIMARY KEY, request TEXT NOT NULL, status TEXT NOT NULL,
                    current_agent TEXT, current_skill TEXT, current_action TEXT,
                    result_json TEXT, error TEXT, metadata_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS agent_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, task_id TEXT NOT NULL,
                    event_type TEXT NOT NULL, data_json TEXT NOT NULL DEFAULT '{}',
                    timestamp TEXT NOT NULL, FOREIGN KEY(task_id) REFERENCES agent_tasks(id)
                );
                CREATE INDEX IF NOT EXISTS idx_agent_events_task ON agent_events(task_id, id);
                CREATE TABLE IF NOT EXISTS crm_leads (
                    id TEXT PRIMARY KEY, name TEXT NOT NULL, email TEXT, phone TEXT,
                    whatsapp TEXT, website TEXT, company TEXT NOT NULL, industry TEXT,
                    country TEXT, language TEXT, source TEXT, status TEXT NOT NULL DEFAULT 'new',
                    score INTEGER NOT NULL DEFAULT 0, tier TEXT NOT NULL DEFAULT 'new',
                    notes TEXT, source_url TEXT NOT NULL DEFAULT '', researched_at TEXT,
                    follow_up_state TEXT NOT NULL DEFAULT 'not_started',
                    next_follow_up_at TEXT, last_contacted_at TEXT, created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL, UNIQUE(company, source_url)
                );
                CREATE INDEX IF NOT EXISTS idx_crm_leads_status ON crm_leads(status);
                CREATE INDEX IF NOT EXISTS idx_crm_leads_score ON crm_leads(score);
                CREATE INDEX IF NOT EXISTS idx_crm_followup ON crm_leads(follow_up_state, next_follow_up_at);
                CREATE TABLE IF NOT EXISTS sales_approvals (
                    id TEXT PRIMARY KEY, task_id TEXT NOT NULL, lead_id TEXT NOT NULL,
                    channel TEXT NOT NULL, payload_json TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending', reviewer TEXT,
                    reviewed_at TEXT, sent_at TEXT, created_at TEXT NOT NULL,
                    FOREIGN KEY(task_id) REFERENCES agent_tasks(id),
                    FOREIGN KEY(lead_id) REFERENCES crm_leads(id)
                );
                CREATE INDEX IF NOT EXISTS idx_sales_approvals_status ON sales_approvals(status);
            """)
            self._ensure_crm_columns(conn)

    @staticmethod
    def _ensure_crm_columns(conn: sqlite3.Connection) -> None:
        existing = {row[1] for row in conn.execute("PRAGMA table_info(crm_leads)")}
        additions = {
            "whatsapp": "TEXT", "website": "TEXT", "source_url": "TEXT NOT NULL DEFAULT ''",
            "researched_at": "TEXT", "follow_up_state": "TEXT NOT NULL DEFAULT 'not_started'",
            "next_follow_up_at": "TEXT", "last_contacted_at": "TEXT",
        }
        for name, definition in additions.items():
            if name not in existing:
                conn.execute(f"ALTER TABLE crm_leads ADD COLUMN {name} {definition}")

    def save_task(self, task: Task) -> None:
        now = datetime.now(timezone.utc)
        task.updated_at = now
        with self._connect() as conn:
            conn.execute("""
                INSERT INTO agent_tasks
                (id,request,status,current_agent,current_skill,current_action,result_json,error,metadata_json,created_at,updated_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(id) DO UPDATE SET status=excluded.status,
                  current_agent=excluded.current_agent,current_skill=excluded.current_skill,
                  current_action=excluded.current_action,result_json=excluded.result_json,
                  error=excluded.error,metadata_json=excluded.metadata_json,updated_at=excluded.updated_at
            """, (
                task.id, task.request, task.status.value, task.current_agent, task.current_skill,
                task.current_action, json.dumps(task.result, ensure_ascii=False, default=str), task.error,
                json.dumps(task.metadata, ensure_ascii=False, default=str), task.created_at.isoformat(), now.isoformat(),
            ))

    def load_task(self, task_id: str) -> Task | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM agent_tasks WHERE id=?", (task_id,)).fetchone()
        if row is None:
            return None
        return Task(
            request=row["request"], id=row["id"], status=TaskStatus(row["status"]),
            current_agent=row["current_agent"], current_skill=row["current_skill"],
            current_action=row["current_action"], result=json.loads(row["result_json"] or "null"),
            error=row["error"], metadata=json.loads(row["metadata_json"] or "{}"),
            created_at=datetime.fromisoformat(row["created_at"]), updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def append_event(self, event: TaskEvent) -> None:
        with self._connect() as conn:
            conn.execute("INSERT INTO agent_events(task_id,event_type,data_json,timestamp) VALUES (?,?,?,?)",
                         (event.task_id, event.event_type, json.dumps(event.data, ensure_ascii=False, default=str), event.timestamp.isoformat()))

    def events_for_task(self, task_id: str) -> list[TaskEvent]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM agent_events WHERE task_id=? ORDER BY id", (task_id,)).fetchall()
        return [TaskEvent(task_id=r["task_id"], event_type=r["event_type"], data=json.loads(r["data_json"]), timestamp=datetime.fromisoformat(r["timestamp"])) for r in rows]

    @staticmethod
    def _lead_key(company: str, source_url: str | None) -> str:
        raw = f"{company.casefold().strip()}|{source_url or ''}".encode("utf-8")
        return hashlib.sha256(raw).hexdigest()[:20].upper()

    def upsert_lead(self, lead: dict[str, Any]) -> dict[str, Any]:
        company = str(lead["company"]).strip()
        source_url = str(lead.get("source_url") or "")
        now = datetime.now(timezone.utc).isoformat()
        lead_id = str(lead.get("id") or f"LEAD-{self._lead_key(company, source_url)}")
        values = (
            lead_id, lead.get("name") or "Business Owner", lead.get("email"), lead.get("phone"),
            lead.get("whatsapp"), lead.get("website"), company, lead.get("industry"), lead.get("country", "Indonesia"),
            lead.get("language", "id"), lead.get("source", "research"), lead.get("status", lead.get("tier", "new")),
            int(lead.get("score", 0)), lead.get("tier", "new"), lead.get("notes"), source_url,
            lead.get("researched_at", now), lead.get("follow_up_state", "not_started"), lead.get("next_follow_up_at"),
            lead.get("last_contacted_at"), now, now,
        )
        with self._connect() as conn:
            conn.execute("""
                INSERT INTO crm_leads
                (id,name,email,phone,whatsapp,website,company,industry,country,language,source,status,score,tier,notes,source_url,researched_at,follow_up_state,next_follow_up_at,last_contacted_at,created_at,updated_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(company, source_url) DO UPDATE SET name=excluded.name,email=excluded.email,
                  phone=excluded.phone,whatsapp=excluded.whatsapp,website=excluded.website,industry=excluded.industry,
                  country=excluded.country,language=excluded.language,source=excluded.source,status=excluded.status,
                  score=excluded.score,tier=excluded.tier,notes=excluded.notes,researched_at=excluded.researched_at,
                  updated_at=excluded.updated_at
            """, values)
            row = conn.execute("SELECT * FROM crm_leads WHERE company=? AND source_url=?", (company, source_url)).fetchone()
        return dict(row)

    def get_lead(self, lead_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM crm_leads WHERE id=?", (lead_id,)).fetchone()
        return dict(row) if row else None

    def due_followups(self, before: str | None = None) -> list[dict[str, Any]]:
        cutoff = before or datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT * FROM crm_leads
                WHERE next_follow_up_at IS NOT NULL
                  AND next_follow_up_at <= ?
                  AND follow_up_state IN ('scheduled', 'queued')
                ORDER BY next_follow_up_at, score DESC
            """, (cutoff,)).fetchall()
        return [dict(row) for row in rows]

    def set_lead_status(self, lead_id: str, status: str) -> None:
        with self._connect() as conn:
            if conn.execute("UPDATE crm_leads SET status=?, updated_at=? WHERE id=?", (status, datetime.now(timezone.utc).isoformat(), lead_id)).rowcount != 1:
                raise ValueError("lead not found")

    def set_followup_state(self, lead_id: str, state: str, *, next_follow_up_at: str | None = None, last_contacted_at: str | None = None) -> None:
        with self._connect() as conn:
            if conn.execute("UPDATE crm_leads SET follow_up_state=?, next_follow_up_at=?, last_contacted_at=COALESCE(?, last_contacted_at), updated_at=? WHERE id=?", (state, next_follow_up_at, last_contacted_at, datetime.now(timezone.utc).isoformat(), lead_id)).rowcount != 1:
                raise ValueError("lead not found")

    def create_approval(self, task_id: str, lead_id: str, channel: str, payload: dict[str, Any]) -> str:
        from uuid import uuid4
        approval_id = f"APR-{uuid4().hex[:12].upper()}"
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute("INSERT INTO sales_approvals(id,task_id,lead_id,channel,payload_json,created_at) VALUES (?,?,?,?,?,?)",
                         (approval_id, task_id, lead_id, channel, json.dumps(payload, ensure_ascii=False), now))
        return approval_id

    def get_approval(self, approval_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM sales_approvals WHERE id=?", (approval_id,)).fetchone()
        if row is None:
            return None
        result = dict(row)
        result["payload"] = json.loads(result.pop("payload_json"))
        return result

    def review_approval(self, approval_id: str, status: str, reviewer: str) -> None:
        if status not in {"approved", "rejected"}:
            raise ValueError("status must be approved or rejected")
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            updated = conn.execute("UPDATE sales_approvals SET status=?, reviewer=?, reviewed_at=? WHERE id=? AND status='pending'", (status, reviewer, now, approval_id)).rowcount
        if updated != 1:
            raise ValueError("approval not found or no longer pending")

    def mark_approval_sent(self, approval_id: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            updated = conn.execute("UPDATE sales_approvals SET status='sent', sent_at=? WHERE id=? AND status='approved'", (now, approval_id)).rowcount
        if updated != 1:
            raise ValueError("approval is not approved or no longer available")
