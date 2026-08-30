from __future__ import annotations

from typing import Any


def rank_maha_hot_leads(leads: list[dict[str, Any]], limit: int = 50) -> list[dict[str, Any]]:
    """Rank research candidates by commercial fit, contactability and research confidence."""
    ranked: list[dict[str, Any]] = []
    for lead in leads:
        score = float(lead.get("score", 0))
        confidence = float(lead.get("research_confidence", 0))
        source_count = int(lead.get("source_count", 1))
        bonus = min(10.0, max(0, source_count - 1) * 5.0)
        hot_score = min(100, round(score * 0.75 + confidence * 15 + bonus))
        tier = "hot" if hot_score >= 80 else "qualified" if hot_score >= 60 else "nurture" if hot_score >= 40 else "reject"
        ranked.append({**lead, "maha_hot_score": hot_score, "maha_tier": tier})
    ranked.sort(key=lambda item: (-item["maha_hot_score"], -float(item.get("research_confidence", 0)), item["company"]))
    return ranked[:limit]
