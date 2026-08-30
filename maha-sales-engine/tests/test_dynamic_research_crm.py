from pathlib import Path

from agent_runtime.crm import CRM
from agent_runtime.store import AgentStore
from research.web_search import discover_bali_businesses


def test_dynamic_research_provider_adapter():
    class FakeProvider:
        def search(self, query: str, limit: int):
            return [{"title": "Bali Sunrise Cafe", "url": "https://example.com/cafe", "snippet": "Cafe in Bali", "email": "hello@example.com", "phone": "+62 812 3456 7890"}]

    results = discover_bali_businesses(limit=1, categories=("cafe",), provider=FakeProvider())
    assert len(results) == 1
    assert results[0]["company"] == "Bali Sunrise Cafe"
    assert results[0]["source"] == "web_search"
    assert results[0]["source_url"] == "https://example.com/cafe"
    assert results[0]["phone"] == "+62 812 3456 7890"
    assert results[0]["email"] == "hello@example.com"


def test_crm_status_and_followup_are_durable(tmp_path: Path):
    db_path = tmp_path / "maha.db"
    store = AgentStore(db_path)
    lead = store.upsert_lead({
        "company": "Test Bali Cafe", "industry": "cafe", "country": "Indonesia",
        "source": "test", "source_url": "https://example.com/test", "score": 70, "tier": "qualified",
    })
    crm = CRM(db_path)
    crm.set_status(lead["id"], "contacted")
    crm.set_followup_state(lead["id"], "scheduled", next_followup_at="2099-01-01T00:00:00+00:00")

    reloaded = crm.get_lead(lead["id"])
    assert reloaded["status"] == "contacted"
    assert reloaded["follow_up_state"] == "scheduled"
    assert reloaded["next_follow_up_at"] == "2099-01-01T00:00:00+00:00"
    assert crm.due_followups("2100-01-01T00:00:00+00:00")[0]["id"] == lead["id"]
