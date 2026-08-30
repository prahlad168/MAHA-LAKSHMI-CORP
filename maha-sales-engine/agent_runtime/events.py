from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Protocol


@dataclass(frozen=True)
class TaskEvent:
    task_id: str
    event_type: str
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class EventSink(Protocol):
    def append_event(self, event: TaskEvent) -> None: ...

    def events_for_task(self, task_id: str) -> list[TaskEvent]: ...


class EventLog:
    """Event log with optional durable sink; memory remains useful for tests."""

    def __init__(self, sink: EventSink | None = None) -> None:
        self._events: list[TaskEvent] = []
        self._sink = sink

    def append(self, event: TaskEvent) -> TaskEvent:
        self._events.append(event)
        if self._sink is not None:
            self._sink.append_event(event)
        return event

    def emit(self, task_id: str, event_type: str, **data: Any) -> TaskEvent:
        return self.append(TaskEvent(task_id=task_id, event_type=event_type, data=data))

    def for_task(self, task_id: str) -> list[TaskEvent]:
        if self._sink is not None:
            return self._sink.events_for_task(task_id)
        return [event for event in self._events if event.task_id == task_id]
