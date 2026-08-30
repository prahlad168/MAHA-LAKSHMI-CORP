from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    WAITING = "waiting"
    PAUSED = "paused"
    FAILED = "failed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


@dataclass
class Task:
    request: str
    id: str = field(default_factory=lambda: str(uuid4()))
    status: TaskStatus = TaskStatus.PENDING
    current_agent: str | None = None
    current_skill: str | None = None
    current_action: str | None = None
    result: Any = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def transition(self, status: TaskStatus) -> None:
        self.status = status
        self.updated_at = datetime.now(timezone.utc)

    def assign(self, *, agent: str | None = None, skill: str | None = None, action: str | None = None) -> None:
        if agent is not None:
            self.current_agent = agent
        if skill is not None:
            self.current_skill = skill
        if action is not None:
            self.current_action = action
        self.updated_at = datetime.now(timezone.utc)
