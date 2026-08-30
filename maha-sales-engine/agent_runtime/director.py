from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .actions import ActionRegistry, ActionRequest, ActionResult
from .agents import AgentRegistry
from .events import EventLog
from .skills import SkillRegistry
from .task import Task, TaskStatus


@dataclass(frozen=True)
class DirectorDecision:
    agent: str
    skill: str | None = None
    action: ActionRequest | None = None


class Director:
    """Small deterministic orchestration kernel for the first MAHA vertical slice."""

    def __init__(self, agents: AgentRegistry, skills: SkillRegistry, actions: ActionRegistry, events: EventLog) -> None:
        self.agents = agents
        self.skills = skills
        self.actions = actions
        self.events = events

    def run_once(self, task: Task, agent_name: str) -> ActionResult | None:
        agent = self.agents.get(agent_name)
        if agent is None:
            task.error = f"Unknown agent: {agent_name}"
            task.transition(TaskStatus.FAILED)
            self.events.emit(task.id, "TASK_FAILED", error=task.error)
            return None

        task.assign(agent=agent_name)
        task.transition(TaskStatus.RUNNING)
        self.events.emit(task.id, "AGENT_STARTED", agent=agent_name)

        request = agent.plan(task)
        if request is None:
            task.transition(TaskStatus.COMPLETED)
            self.events.emit(task.id, "TASK_COMPLETED", result=task.result)
            return None

        task.assign(action=request.name)
        self.events.emit(task.id, "ACTION_REQUESTED", action=request.name, parameters=request.parameters)
        result = self.actions.execute(request)
        if result.success:
            task.result = result.data
            self.events.emit(task.id, "ACTION_EXECUTED", action=request.name)
            task.transition(TaskStatus.COMPLETED)
            self.events.emit(task.id, "TASK_COMPLETED", result=result.data)
        else:
            task.error = result.error
            self.events.emit(task.id, "ACTION_FAILED", action=request.name, error=result.error)
            task.transition(TaskStatus.FAILED)
        return result
