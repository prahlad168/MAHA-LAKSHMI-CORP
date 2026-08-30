from maha_sales_engine.agent_runtime import (
    ActionRegistry,
    Agent,
    AgentRegistry,
    Director,
    EventLog,
    SkillRegistry,
    Task,
    TaskStatus,
)
from maha_sales_engine.agent_runtime.actions import ActionRequest


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
