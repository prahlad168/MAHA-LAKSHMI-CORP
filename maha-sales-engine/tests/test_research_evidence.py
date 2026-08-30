from pathlib import Path

from agent_runtime.evidence_store import LeadEvidenceStore
from agent_runtime.sales_runtime_v3 import build_sales_runtime_v3


class FakeContentEngine:
    def generate_whatsapp_content(self, template_type, lead):
        return f"Hello {lead['company']}"


def test_research_evidence_is_persisted(tmp_path: Path):
    db = tmp_path / "maha.db"
    runtime = build_sales_runtime_v3(db, FakeContentEngine())
    task = runtime.run(
        "research test",
        [{
            "company": "Example Bali Cafe",
            "industry": "cafe",
            "country": "Indonesia",
            "phone": "+628123456789",
            "website": "https://example.com",
            "source": "bing",
            "source_url": "https://example.com/result",
            "research_confidence": 0.9,
            "source_count": 2,
            "maha_hot_score": 88,
            "maha_tier": "hot",
            "sources": [{"provider": "bing", "source_type": "search", "url": "https://example.com/result", "title": "Example Bali Cafe", "snippet": "Cafe in Bali", "quality": 0.8}],
            "contact_pages": ["https://example.com/contact"],
            "discovered_emails": ["hello@example.com"],
            "discovered_phones": ["+628123456789"],
            "whatsapp_urls": ["https://wa.me/628123456789"],
            "research_snippet": "Cafe in Bali",
            "research_host": "example.com",
            "enrichment_status": "enriched",
            "enrichment_confidence": 0.95,
        }],
    )

    assert task.status.value == "waiting"
    store = LeadEvidenceStore(db)
    rows = store.list_for_lead(task.result[0]["lead_id"] if task.result else "")
    # The task result is an approval batch; lead id is retrieved from the approval payload in practice.
    # This assertion uses the first CRM lead present in the same database.
    import sqlite3
    with sqlite3.connect(db) as conn:
        lead_id = conn.execute("SELECT id FROM crm_leads LIMIT 1").fetchone()[0]
    rows = store.list_for_lead(lead_id)
    types = {row["evidence_type"] for row in rows}
    assert {"source", "contact_page", "email", "phone", "whatsapp"}.issubset(types)
