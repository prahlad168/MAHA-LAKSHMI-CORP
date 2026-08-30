from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .actions import ActionRequest, ActionResult, ActionRegistry
from .task import Task


AgentHandler = Callable[[Task], ActionRequest | None]


@dataclass
class Agent:
    name: str
    handler: AgentHandler

    def plan(self, task: Task) -> ActionRequest | None:
        return self.handler(task)


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, Agent] = {}

    def register(self, agent: Agent) -> None:
        if not agent.name or agent.name in self._agents:
            raise ValueError(f"Invalid or duplicate agent: {agent.name!r}")
        self._agents[agent.name] = agent

    def get(self, name: str) -> Agent | None:
        return self._agents.get(name)

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._agents))
