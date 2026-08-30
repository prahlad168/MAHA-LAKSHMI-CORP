from pathlib import Path

from agent_runtime import TaskStatus, build_sales_runtime


def test_research_lead_generation_sales_slice(tmp_path: Path):
    db_path = tmp_path / "maha.db"
    runtime = build_sales_runtime(db_path)
    candidates = [
        {"name": "Made", "company": "Cafe Bali", "industry": "cafe", "phone": "+62812", "country": "Indonesia"},
        {"name": "Wayan", "company": "Hotel Ubud", "industry": "hotel", "email": "hello@example.com", "country": "Indonesia"},
        {"company": "Cafe Bali", "industry": "cafe", "phone": "+62813", "country": "Indonesia"},
        {"company": "", "industry": "retail"},
    ]

    task = runtime.run("Find suitable Bali businesses for WhatsApp Marketing Kit", candidates)

    assert task.status is TaskStatus.COMPLETED
    assert len(task.result) == 2
    assert task.result[0]["company"] == "Cafe Bali"
    assert task.result[0]["channel"] == "whatsapp"
    assert "WhatsApp Marketing Kit" in task.result[0]["message"]

    events = runtime.events.for_task(task.id)
    assert [event.event_type for event in events] == [
        "AGENT_STARTED",
        "ACTION_REQUESTED",
        "ACTION_EXECUTED",
        "AGENT_STARTED",
        "ACTION_REQUESTED",
        "ACTION_EXECUTED",
        "TASK_COMPLETED",
    ]
