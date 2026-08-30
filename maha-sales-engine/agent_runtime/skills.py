from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .task import Task


SkillHandler = Callable[[Task], dict[str, Any]]


@dataclass
class Skill:
    name: str
    handler: SkillHandler
    version: str = "1.0.0"

    def run(self, task: Task) -> dict[str, Any]:
        return self.handler(task)


class SkillRegistry:
    def __init__(self) -> None:
        self._skills: dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        if not skill.name or skill.name in self._skills:
            raise ValueError(f"Invalid or duplicate skill: {skill.name!r}")
        self._skills[skill.name] = skill

    def get(self, name: str) -> Skill | None:
        return self._skills.get(name)

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._skills))
