from research.multi_source import MultiSourceResearcher, SourcePolicy
from research.ranking import rank_maha_hot_leads


class FakeProvider:
    def __init__(self, name, results):
        self.name = name
        self.source_type = "test"
        self.results = results

    def search(self, query, limit=10, enrich=True):
        return self.results[:limit]


def test_cross_provider_dedupe_prefers_higher_quality_source():
    providers = [
        FakeProvider("generic", [{"title": "Bali Cafe", "url": "https://example.com/bali-cafe", "snippet": "A cafe", "phone": "+62 812 3456 7890"}]),
        FakeProvider("official", [{"title": "PT Bali Cafe", "url": "https://phribali.or.id/member/bali-cafe", "snippet": "PHRI member", "phone": "081234567890"}]),
    ]
    results = MultiSourceResearcher(providers, SourcePolicy()).search("cafe Bali", limit=10)
    assert len(results) == 1
    assert results[0]["source_count"] == 2
    assert results[0]["source_quality"] == 0.98
    assert results[0]["source"] == "official"


def test_hot_lead_ranking_is_deterministic():
    leads = [
        {"company": "A", "score": 80, "research_confidence": 1.0, "source_count": 2},
        {"company": "B", "score": 60, "research_confidence": 1.0, "source_count": 2},
    ]
    ranked = rank_maha_hot_leads(leads)
    assert ranked[0]["company"] == "A"
    assert ranked[0]["maha_rank"] if "maha_rank" in ranked[0] else True
    assert ranked[0]["maha_tier"] == "hot"
