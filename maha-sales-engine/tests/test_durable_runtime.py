from pathlib import Path

from maha_sales_engine.agent_runtime.real_research import build_default_content_engine
from maha_sales_engine.agent_runtime.store import AgentStore
from maha_sales_engine.agent_runtime.task import Task, TaskStatus
from maha_sales_engine.agent_runtime.vertical_slice import build_sales_runtime


def test_task_and_events_survive_new_store_instance(tmp_path: Path):
    db = tmp_path / "runtime.db"
    store = AgentStore(db)
    task = Task("persist me")
    store.save_task(task)
    store.append_event(__import__("maha_sales_engine.agent_runtime.events", fromlist=["TaskEvent"]).TaskEvent(task.id, "TASK_CREATED"))

    restored = AgentStore(db)
    loaded = restored.load_task(task.id)
    events = restored.events_for_task(task.id)

    assert loaded is not None
    assert loaded.request == "persist me"
    assert events[0].event_type == "TASK_CREATED"


def test_real_bali_seed_reaches_human_approval(tmp_path: Path):
    runtime = build_sales_runtime(tmp_path / "sales.db", build_default_content_engine())
    task = runtime.run(
        "prepare Bali outreach",
        [{
            "company": "Bali Test Cafe", "name": "Made", "phone": "+628123456789",
            "industry": "cafe", "country": "Indonesia", "source": "test",
            "source_url": "test://bali-test-cafe",
        }],
    )

    assert task.status is TaskStatus.WAITING
    assert task.result
    approval_id = task.result[0]["approval_id"]
    approval = runtime.store.get_approval(approval_id)
    assert approval is not None
    assert approval["status"] == "pending"
    assert "MAHA LAKSHMI" in approval["payload"]["message"]
