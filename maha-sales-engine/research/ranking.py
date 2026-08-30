from __future__ import annotations

from typing import Any


def rank_maha_hot_leads(leads: list[dict[str, Any]], limit: int = 50) -> list[dict[str, Any]]:
    """Rank candidates using business fit, contactability, research corroboration and enrichment."""
    ranked: list[dict[str, Any]] = []
    for lead in leads:
        explicit_score = lead.get("score")
        source_quality = float(lead.get("source_quality", 0.0))
        base_score = float(explicit_score) if explicit_score is not None else source_quality * 70.0
        confidence = float(lead.get("research_confidence", 0))
        enrichment = float(lead.get("enrichment_confidence", 0))
        source_count = int(lead.get("source_count", 1))
        corroboration = min(10.0, max(0, source_count - 1) * 5.0)
        contactability = 0.0
        contactability += 5.0 if lead.get("phone") else 0
        contactability += 5.0 if lead.get("email") else 0
        contactability += 5.0 if lead.get("whatsapp") else 0
        composite = round(
            base_score * 0.65
            + confidence * 10
            + enrichment * 10
            + corroboration
            + contactability
        )
        hot_score = min(100, max(round(base_score), composite))
        tier = "hot" if hot_score >= 80 else "qualified" if hot_score >= 60 else "nurture" if hot_score >= 40 else "reject"
        ranked.append({**lead, "maha_hot_score": hot_score, "maha_tier": tier})
    ranked.sort(
        key=lambda item: (
            -item["maha_hot_score"],
            -float(item.get("enrichment_confidence", 0)),
            -float(item.get("research_confidence", 0)),
            item["company"],
        )
    )
    return ranked[:limit]
