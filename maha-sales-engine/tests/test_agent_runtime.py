from pathlib import Path

from agent_runtime import (
    ActionRegistry,
    Agent,
    AgentRegistry,
    Director,
    EventLog,
    SkillRegistry,
    Task,
    TaskStatus,
)
from agent_runtime.actions import ActionRequest
from agent_runtime.vertical_slice import build_sales_runtime


def test_task_lifecycle_and_event_log():
    actions = ActionRegistry()
    actions.register("echo", lambda params: params["value"])

    agents = AgentRegistry()
    agents.register(Agent("research", lambda task: ActionRequest("echo", {"value": task.request})))

    events = EventLog()
    director = Director(agents, SkillRegistry(), actions, events)
    task = Task("find ten Bali businesses")

    result = director.run_once(task, "research")

    assert result is not None and result.success
    assert task.status is TaskStatus.COMPLETED
    assert task.result == "find ten Bali businesses"
    assert [event.event_type for event in events.for_task(task.id)] == [
        "AGENT_STARTED",
        "ACTION_REQUESTED",
        "ACTION_EXECUTED",
        "TASK_COMPLETED",
    ]


def test_unknown_action_fails_task():
    actions = ActionRegistry()
    agents = AgentRegistry()
    agents.register(Agent("research", lambda task: ActionRequest("missing")))

    events = EventLog()
    director = Director(agents, SkillRegistry(), actions, events)
    task = Task("test")

    result = director.run_once(task, "research")

    assert result is not None and not result.success
    assert task.status is TaskStatus.FAILED
    assert "Unknown action" in (task.error or "")


def test_sales_runtime_uses_content_engine(tmp_path: Path):
    class FakeContentEngine:
        def generate_whatsapp_content(self, template_type, lead):
            assert template_type == "whatsapp_initial"
            return f"CONTENT-ENGINE:{lead['company']}"

    runtime = build_sales_runtime(tmp_path / "maha.db", FakeContentEngine())
    task = runtime.run(
        "prepare outreach",
        [{"name": "Made", "company": "Bali Cafe", "phone": "0812", "industry": "cafe"}],
    )

    assert task.status is TaskStatus.COMPLETED
    assert task.result[0]["message"] == "CONTENT-ENGINE:Bali Cafe"
