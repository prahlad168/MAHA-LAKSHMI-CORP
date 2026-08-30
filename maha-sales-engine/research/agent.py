from __future__ import annotations

from pathlib import Path
from typing import Any

from .bing_search import BingResearchProvider
from .multi_source import MultiSourceResearcher, SourcePolicy
from .ranking import rank_maha_hot_leads
from .web_search import DuckDuckGoResearchProvider


class ResearchAgent:
    """Business research coordinator for MAHA lead discovery."""

    def __init__(self, providers: list[Any] | None = None, policy: SourcePolicy | None = None) -> None:
        self.providers = providers or [DuckDuckGoResearchProvider(), BingResearchProvider()]
        self.researcher = MultiSourceResearcher(self.providers, policy=policy)

    def run(self, *, limit: int = 10, categories: tuple[str, ...] = ("restaurant", "cafe", "hotel", "tour operator")) -> list[dict[str, Any]]:
        if not 1 <= limit <= 50:
            raise ValueError("limit must be between 1 and 50")
        per_category = max(3, min(12, (limit + len(categories) - 1) // len(categories) + 2))
        merged: dict[tuple[str, str], dict[str, Any]] = {}
        for category in categories:
            query = f"{category} Bali Indonesia business"
            for item in self.researcher.search(query, limit=per_category):
                key = (self.researcher._name_key(str(item.get("company", ""))), str(item.get("website") or item.get("source_url") or ""))
                existing = merged.get(key)
                if existing is None or float(item.get("research_confidence", 0)) > float(existing.get("research_confidence", 0)):
                    merged[key] = item
                elif existing is not None:
                    existing["source_count"] = max(int(existing.get("source_count", 1)), int(item.get("source_count", 1)))
        leads = rank_maha_hot_leads(list(merged.values()), limit=limit)
        for rank, lead in enumerate(leads, start=1):
            lead["maha_rank"] = rank
        return leads
