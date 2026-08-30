from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class QualificationPolicy:
    """Transparent V1 lead-scoring policy; no LLM is required to score a lead."""

    hot_threshold: int = 80
    qualified_threshold: int = 60
    nurture_threshold: int = 40


def qualify_lead(lead: dict[str, Any], policy: QualificationPolicy | None = None) -> dict[str, Any]:
    policy = policy or QualificationPolicy()
    score = 0
    industry = str(lead.get("industry", "")).casefold()
    country = str(lead.get("country", "")).casefold()

    if lead.get("phone"):
        score += 25
    if lead.get("email"):
        score += 20
    if industry in {"restaurant", "cafe", "hotel", "tour", "tour operator", "retail", "store"}:
        score += 20
    if country == "indonesia":
        score += 15
    if lead.get("website"):
        score += 10
    if lead.get("whatsapp"):
        score += 10

    score = min(score, 100)
    if score >= policy.hot_threshold:
        tier = "hot"
    elif score >= policy.qualified_threshold:
        tier = "qualified"
    elif score >= policy.nurture_threshold:
        tier = "nurture"
    else:
        tier = "reject"

    return {**lead, "score": score, "tier": tier}
