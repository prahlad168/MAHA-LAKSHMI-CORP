import sqlite3
from pathlib import Path

from agent_runtime.events import TaskEvent
from agent_runtime.intelligence import CRMIntelligence
from agent_runtime.sales_runtime_v3 import build_sales_runtime_v3
from agent_runtime.store import AgentStore
from agent_runtime.task import Task
from research.enrichment import WebsiteEnricher


class FakeContentEngine:
    def generate_whatsapp_content(self, template_type, lead):
        return f"Hello {lead['company']}"


def test_database_restart_resume_preserves_task_and_events(tmp_path: Path):
    db = tmp_path / "maha.db"
    store = AgentStore(db)
    task = Task("restart test")
    store.save_task(task)
    store.append_event(TaskEvent(task.id, "TASK_CREATED"))

    reloaded_store = AgentStore(db)
    loaded = reloaded_store.load_task(task.id)
    events = reloaded_store.events_for_task(task.id)

    assert loaded is not None
    assert loaded.id == task.id
    assert loaded.request == "restart test"
    assert [event.event_type for event in events] == ["TASK_CREATED"]


def test_research_enrichment_and_crm_intelligence_smoke(tmp_path: Path):
    class FakeEnricher(WebsiteEnricher):
        def _fetch(self, url):
            return (
                '<html><a href="/contact">Contact</a>'
                '<a href="https://wa.me/628123456789">WhatsApp</a>'
                'hello@example.com +62 812-3456-7890</html>',
                "https://example.com/",
            )

    lead = FakeEnricher().enrich({
        "company": "Example Bali Cafe", "industry": "cafe", "country": "Indonesia",
        "website": "https://example.com/", "source": "test",
        "source_url": "https://example.com/result", "research_confidence": 0.9, "source_count": 2,
    })

    assert lead["enrichment_status"] == "enriched"
    assert lead["discovered_emails"] == ["hello@example.com"]
    assert lead["discovered_phones"] == ["+6281234567890"]
    assert lead["whatsapp_urls"] == ["https://wa.me/628123456789"]
    assert lead["contact_pages"] == ["https://example.com/contact"]

    db = tmp_path / "sales.db"
    runtime = build_sales_runtime_v3(db, FakeContentEngine())
    task = runtime.run("integration", [{**lead, "maha_hot_score": 88, "maha_tier": "hot"}])
    assert task.status.value == "waiting"

    with sqlite3.connect(db) as conn:
        lead_id = conn.execute("SELECT id FROM crm_leads LIMIT 1").fetchone()[0]
    intelligence = CRMIntelligence(AgentStore(db)).get_lead_intelligence(lead_id)
    assert intelligence["evidence_count"] >= 4
    assert intelligence["latest_evidence_at"]
    assert intelligence["outreach_decision"]["decision"] in {"READY_FOR_HUMAN_APPROVAL", "RESEARCH_REQUIRED"}
