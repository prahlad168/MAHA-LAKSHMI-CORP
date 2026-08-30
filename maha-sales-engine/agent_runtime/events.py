from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class TaskEvent:
    task_id: str
    event_type: str
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class EventLog:
    """Append-only in-memory event log for V1; persistence is injected later."""

    def __init__(self) -> None:
        self._events: list[TaskEvent] = []

    def append(self, event: TaskEvent) -> TaskEvent:
        self._events.append(event)
        return event

    def emit(self, task_id: str, event_type: str, **data: Any) -> TaskEvent:
        return self.append(TaskEvent(task_id=task_id, event_type=event_type, data=data))

    def for_task(self, task_id: str) -> list[TaskEvent]:
        return [event for event in self._events if event.task_id == task_id]
