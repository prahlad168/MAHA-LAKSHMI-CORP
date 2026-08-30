from datetime import datetime, timezone
from pathlib import Path

from agent_runtime.evidence_store import LeadEvidenceStore
from agent_runtime.intelligence import CRMIntelligence, IntelligencePolicy
from agent_runtime.store import AgentStore


def test_crm_intelligence_explains_score_and_evidence(tmp_path: Path):
    db = tmp_path / "maha.db"
    store = AgentStore(db)
    lead = store.upsert_lead({
        "company": "Bali Hot Cafe",
        "industry": "cafe",
        "country": "Indonesia",
        "source": "bing",
        "source_url": "https://example.com",
        "score": 87,
        "tier": "hot",
        "source_count": 2,
        "research_confidence": 1.0,
        "enrichment_confidence": 0.9,
        "phone": "+6281234567890",
        "whatsapp": "https://wa.me/6281234567890",
    })
    evidence = LeadEvidenceStore(db)
    evidence.save(lead["id"], {
        **lead,
        "sources": [{"provider": "bing", "source_type": "search", "url": "https://example.com", "title": "Bali Hot Cafe", "quality": 0.8}],
        "contact_pages": ["https://example.com/contact"],
        "discovered_phones": ["+6281234567890"],
        "whatsapp_urls": ["https://wa.me/6281234567890"],
        "enrichment_status": "enriched",
    })

    intelligence = CRMIntelligence(store, evidence)
    report = intelligence.explain_lead(lead["id"])

    assert report["score"] == 87
    assert report["evidence_counts"]["source"] == 1
    assert report["evidence_counts"]["contact_page"] == 1
    assert report["evidence_counts"]["whatsapp"] == 1
    assert any("87" in reason for reason in report["score_explanation"])


def test_crm_intelligence_blocks_stale_lead(tmp_path: Path):
    db = tmp_path / "maha.db"
    store = AgentStore(db)
    lead = store.upsert_lead({
        "company": "Old Bali Cafe",
        "industry": "cafe",
        "country": "Indonesia",
        "source": "test",
        "source_url": "https://example.com",
        "score": 90,
        "tier": "hot",
        "source_count": 1,
        "enrichment_confidence": 0.9,
        "phone": "+6281234567890",
    })
    evidence = LeadEvidenceStore(db)
    evidence.save(lead["id"], {**lead, "sources": [{"url": "https://example.com", "title": "Old Bali Cafe", "quality": 0.8}]})

    intelligence = CRMIntelligence(store, evidence, IntelligencePolicy(evidence_fresh_days=7))
    decision = intelligence.outreach_decision(
        lead["id"], now=datetime.now(timezone.utc).replace(year=2000)
    )

    assert decision["allowed"] is False
    assert decision["decision"] == "RESEARCH_REQUIRED"
    assert decision["needs_research"] is True
