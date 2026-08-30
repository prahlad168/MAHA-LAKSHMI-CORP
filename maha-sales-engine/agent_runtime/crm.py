from __future__ import annotations

from pathlib import Path
from typing import Any

from .store import AgentStore


CRM_STATUSES = {
    "new",
    "researched",
    "qualified",
    "nurture",
    "contacted",
    "replied",
    "interested",
    "proposal",
    "won",
    "lost",
    "do_not_contact",
}

FOLLOWUP_STATES = {
    "not_started",
    "queued",
    "awaiting_approval",
    "scheduled",
    "sent",
    "replied",
    "completed",
    "stopped",
}


class CRMError(ValueError):
    pass


class CRM:
    """Small CRM facade over AgentStore for lifecycle-safe lead management."""

    def __init__(self, db_path: Path):
        self.store = AgentStore(db_path)

    def upsert_researched_lead(self, lead: dict[str, Any]) -> dict[str, Any]:
        return self.store.upsert_lead({**lead, "status": "researched"})

    def set_status(self, lead_id: str, status: str) -> None:
        if status not in CRM_STATUSES:
            raise CRMError(f"invalid CRM status: {status}")
        self.store.set_lead_status(lead_id, status)

    def set_followup_state(self, lead_id: str, state: str, *, next_followup_at: str | None = None) -> None:
        if state not in FOLLOWUP_STATES:
            raise CRMError(f"invalid follow-up state: {state}")
        self.store.set_followup_state(lead_id, state, next_followup_at=next_followup_at)
