from __future__ import annotations

from typing import Any

from .bing_search import BingResearchProvider
from .enrichment import WebsiteEnricher
from .multi_source import MultiSourceResearcher, SourcePolicy
from .ranking import rank_maha_hot_leads
from .web_search import DuckDuckGoResearchProvider

SOURCE_QUERIES: dict[str, tuple[str, ...]] = {
    "tour operator": (
        'site:asitabali.org Bali tour travel member',
        'site:asita.or.id Bali travel company',
        'tour operator Bali Indonesia business',
    ),
    "hotel": (
        'site:phribali.or.id Bali hotel member',
        'hotel Bali Indonesia business',
    ),
    "restaurant": (
        'site:phribali.or.id Bali restaurant member',
        'restaurant Bali Indonesia business',
    ),
    "cafe": (
        'site:phribali.or.id Bali restaurant cafe member',
        'cafe Bali Indonesia business',
    ),
}


class ResearchAgentV2:
    """Multi-source discovery + deep public-site enrichment + Hot Lead ranking."""

    def __init__(
        self,
        providers: list[Any] | None = None,
        policy: SourcePolicy | None = None,
        enricher: WebsiteEnricher | None = None,
    ) -> None:
        self.providers = providers or [DuckDuckGoResearchProvider(), BingResearchProvider()]
        self.researcher = MultiSourceResearcher(self.providers, policy=policy)
        self.enricher = enricher or WebsiteEnricher()

    def run(
        self,
        *,
        limit: int = 10,
        categories: tuple[str, ...] = tuple(SOURCE_QUERIES.keys()),
        enrich: bool = True,
    ) -> list[dict[str, Any]]:
        if not 1 <= limit <= 50:
            raise ValueError("limit must be between 1 and 50")
        per_query = max(3, min(10, limit))
        merged: dict[str, dict[str, Any]] = {}
        for category in categories:
            queries = SOURCE_QUERIES.get(category, (f"{category} Bali Indonesia business",))
            for query in queries:
                for item in self.researcher.search(query, limit=per_query):
                    item["industry"] = category
                    key = self.researcher._name_key(str(item.get("company", "")))
                    if not key:
                        continue
                    existing = merged.get(key)
                    if existing is None:
                        merged[key] = item
                    else:
                        sources = existing.setdefault("sources", [])
                        for source in item.get("sources", []):
                            if source not in sources:
                                sources.append(source)
                        existing["source_count"] = len(sources)
                        existing["source_quality"] = max(float(existing.get("source_quality", 0)), float(item.get("source_quality", 0)))
                        for field in ("phone", "email", "website", "source_url"):
                            if not existing.get(field) and item.get(field):
                                existing[field] = item[field]

        candidates = list(merged.values())
        if enrich:
            candidates = [self.enricher.enrich(lead) for lead in candidates]
        ranked = rank_maha_hot_leads(candidates, limit=limit)
        for rank, lead in enumerate(ranked, start=1):
            lead["maha_rank"] = rank
        return ranked
