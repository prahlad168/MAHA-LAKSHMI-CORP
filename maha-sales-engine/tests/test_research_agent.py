from research.agent import ResearchAgent


class FakeProvider:
    def __init__(self, name, results):
        self.name = name
        self.source_type = "test"
        self.results = results

    def search(self, query, limit=10, enrich=True):
        return self.results[:limit]


def test_research_agent_merges_sources_and_ranks():
    provider_a = FakeProvider(
        "generic",
        [{"title": "Bali Sunrise Cafe", "url": "https://example.com/a", "snippet": "Cafe Bali", "phone": "081234567890"}],
    )
    provider_b = FakeProvider(
        "official",
        [{"title": "PT Bali Sunrise Cafe", "url": "https://phribali.or.id/member/sunrise", "snippet": "PHRI member", "phone": "+6281234567890"}],
    )
    agent = ResearchAgent(providers=[provider_a, provider_b])
    leads = agent.run(limit=10, categories=("cafe",))
    assert len(leads) == 1
    assert leads[0]["source_count"] == 2
    assert leads[0]["source_quality"] == 0.98
    assert leads[0]["maha_rank"] == 1
    assert leads[0]["maha_tier"] in {"hot", "qualified"}
