from __future__ import annotations

from typing import Any

from .bing_search import BingResearchProvider
from .multi_source import MultiSourceResearcher, SourcePolicy
from .ranking import rank_maha_hot_leads
from .web_search import DuckDuckGoResearchProvider


SOURCE_QUERIES: dict[str, tuple[str, ...]] = {
    "tour operator": (
        'site:asitabali.org "Bali" tour travel member',
        'site:asita.or.id "Bali" travel company',
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


class ResearchAgent:
    """Multi-source research coordinator with quality weighting and Hot Lead ranking."""

    def __init__(self, providers: list[Any] | None = None, policy: SourcePolicy | None = None) -> None:
        self.providers = providers or [DuckDuckGoResearchProvider(), BingResearchProvider()]
        self.researcher = MultiSourceResearcher(self.providers, policy=policy)

    def run(
        self,
        *,
        limit: int = 10,
        categories: tuple[str, ...] = ("restaurant", "cafe", "hotel", "tour operator"),
    ) -> list[dict[str, Any]]:
        if not 1 <= limit <= 50:
            raise ValueError("limit must be between 1 and 50")
        per_query = max(3, min(10, limit))
        merged: dict[str, dict[str, Any]] = {}

        for category in categories:
            queries = SOURCE_QUERIES.get(category, (f"{category} Bali Indonesia business",))
            for query in queries:
                for item in self.researcher.search(query, limit=per_query):
                    company_key = self.researcher._name_key(str(item.get("company", "")))
                    domain = str(item.get("website") or item.get("source_url") or "").casefold()
                    key = company_key or domain
                    if not key:
                        continue
                    existing = merged.get(key)
                    if existing is None:
                        merged[key] = item
                        continue
                    existing_sources = existing.setdefault("sources", [])
                    for source in item.get("sources", []):
                        if source not in existing_sources:
                            existing_sources.append(source)
                    existing["source_count"] = len(existing_sources)
                    existing["source_quality"] = max(
                        float(existing.get("source_quality", 0.0)),
                        float(item.get("source_quality", 0.0)),
                    )
                    existing["research_confidence"] = min(
                        1.0,
                        float(existing["source_quality"]) + 0.05 * max(0, existing["source_count"] - 1),
                    )
                    for field in ("phone", "email", "website", "source_url"):
                        if not existing.get(field) and item.get(field):
                            existing[field] = item[field]

        ranked = rank_maha_hot_leads(list(merged.values()), limit=limit)
        for rank, lead in enumerate(ranked, start=1):
            lead["maha_rank"] = rank
        return ranked
