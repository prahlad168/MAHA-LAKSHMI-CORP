from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from .store import AgentStore


@dataclass(frozen=True)
class IntelligencePolicy:
    evidence_fresh_days: int = 7
    hot_score_threshold: int = 80
    min_source_count: int = 1
    min_enrichment_confidence: float = 0.45


class CRMIntelligence:
    """Explainable lead intelligence built on CRM rows and stored evidence."""

    def __init__(self, store: AgentStore, policy: IntelligencePolicy | None = None) -> None:
        self.store = store
        self.policy = policy or IntelligencePolicy()

    def explain_lead(self, lead_id: str) -> dict[str, Any]:
        lead = self.store.get_lead(lead_id)
        if not lead:
            raise ValueError("lead not found")
        evidence = self.store.get_lead_evidence(lead_id)
        evidence_types: dict[str, int] = {}
        latest_at: datetime | None = None
        for item in evidence:
            evidence_types[item["evidence_type"]] = evidence_types.get(item["evidence_type"], 0) + 1
            try:
                ts = datetime.fromisoformat(item["captured_at"])
                latest_at = max(latest_at, ts) if latest_at else ts
            except (TypeError, ValueError):
                pass

        reasons: list[str] = []
        score = int(lead.get("score") or 0)
        if score >= self.policy.hot_score_threshold:
            reasons.append(f"MAHA Hot Score is {score} (>= {self.policy.hot_score_threshold})")
        elif score >= 60:
            reasons.append(f"MAHA score is {score}, above qualified threshold")
        else:
            reasons.append(f"MAHA score is {score}, below hot threshold")
        if evidence_types.get("source", 0):
            reasons.append(f"{evidence_types['source']} research source(s) recorded")
        if evidence_types.get("contact_page", 0):
            reasons.append(f"{evidence_types['contact_page']} contact/about page(s) checked")
        if evidence_types.get("whatsapp", 0):
            reasons.append("public WhatsApp evidence found")
        if evidence_types.get("phone", 0):
            reasons.append("public phone evidence found")
        if evidence_types.get("email", 0):
            reasons.append("public email evidence found")

        return {
            "lead": lead,
            "score_explanation": reasons,
            "evidence_counts": evidence_types,
            "evidence_count": len(evidence),
            "latest_evidence_at": latest_at.isoformat() if latest_at else None,
            "evidence": evidence,
        }

    def outreach_decision(self, lead_id: str, now: datetime | None = None) -> dict[str, Any]:
        now = now or datetime.now(timezone.utc)
        report = self.explain_lead(lead_id)
        lead = report["lead"]
        latest_raw = report["latest_evidence_at"]
        latest = datetime.fromisoformat(latest_raw) if latest_raw else None
        reasons: list[str] = []

        fresh = bool(latest and now - latest <= timedelta(days=self.policy.evidence_fresh_days))
        sufficiently_enriched = float(lead.get("research_confidence") or 0.0) >= 0.0 and (
            bool(lead.get("whatsapp")) or bool(lead.get("phone")) or bool(lead.get("email"))
        )
        has_source = int(lead.get("source_count") or 0) >= self.policy.min_source_count
        score_ok = int(lead.get("score") or 0) >= self.policy.hot_score_threshold
        tier_ok = str(lead.get("tier") or "").lower() in {"hot", "qualified"}

        if not fresh:
            reasons.append("evidence is stale or no evidence timestamp exists")
        if not has_source:
            reasons.append("insufficient source corroboration")
        if not sufficiently_enriched:
            reasons.append("no usable public contact evidence")
        if not score_ok:
            reasons.append(f"score below hot threshold ({self.policy.hot_score_threshold})")
        if not tier_ok:
            reasons.append("lead tier is not outreach-eligible")

        needs_research = not fresh or not has_source or not sufficiently_enriched
        allowed = fresh and has_source and sufficiently_enriched and score_ok and tier_ok
        return {
            "lead_id": lead_id,
            "allowed": allowed,
            "decision": "READY_FOR_HUMAN_APPROVAL" if allowed else "RESEARCH_REQUIRED",
            "needs_research": needs_research,
            "latest_evidence_at": latest_raw,
            "freshness_window_days": self.policy.evidence_fresh_days,
            "reasons": reasons or ["evidence is fresh and lead meets outreach policy"],
        }

    def get_lead_intelligence(self, lead_id: str, now: datetime | None = None) -> dict[str, Any]:
        explanation = self.explain_lead(lead_id)
        decision = self.outreach_decision(lead_id, now=now)
        return {**explanation, "outreach_decision": decision}
