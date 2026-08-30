from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True)
class ActionRequest:
    name: str
    parameters: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ActionResult:
    success: bool
    data: Any = None
    error: str | None = None


ActionHandler = Callable[[dict[str, Any]], Any]


class ActionRegistry:
    def __init__(self) -> None:
        self._handlers: dict[str, ActionHandler] = {}

    def register(self, name: str, handler: ActionHandler) -> None:
        if not name or name in self._handlers:
            raise ValueError(f"Invalid or duplicate action: {name!r}")
        self._handlers[name] = handler

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._handlers))

    def execute(self, request: ActionRequest) -> ActionResult:
        handler = self._handlers.get(request.name)
        if handler is None:
            return ActionResult(False, error=f"Unknown action: {request.name}")
        try:
            return ActionResult(True, data=handler(request.parameters))
        except Exception as exc:
            return ActionResult(False, error=str(exc))
