from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from .evidence_store import LeadEvidenceStore
from .store import AgentStore


@dataclass(frozen=True)
class IntelligencePolicy:
    evidence_fresh_days: int = 7
    hot_score_threshold: int = 80
    min_source_count: int = 1
    min_enrichment_confidence: float = 0.45


class CRMIntelligence:
    """Explainable lead intelligence built on CRM rows and durable evidence."""

    def __init__(self, store: AgentStore, evidence_store: LeadEvidenceStore | None = None,
                 policy: IntelligencePolicy | None = None) -> None:
        self.store = store
        self.evidence = evidence_store or LeadEvidenceStore(store.db_path)
        self.policy = policy or IntelligencePolicy()

    def explain_lead(self, lead_id: str) -> dict[str, Any]:
        lead = self.store.get_lead(lead_id)
        if not lead:
            raise ValueError("lead not found")
        evidence = self.evidence.list_for_lead(lead_id)
        counts: dict[str, int] = {}
        latest_at: datetime | None = None
        for item in evidence:
            kind = item["evidence_type"]
            counts[kind] = counts.get(kind, 0) + 1
            try:
                ts = datetime.fromisoformat(item["captured_at"])
                latest_at = max(latest_at, ts) if latest_at else ts
            except (TypeError, ValueError):
                continue

        reasons: list[str] = []
        score = int(lead.get("score") or 0)
        reasons.append(f"MAHA Hot Score is {score}")
        if counts.get("source"):
            reasons.append(f"{counts['source']} research source(s) recorded")
        if counts.get("source") and int(lead.get("source_count") or 0) > 1:
            reasons.append(f"cross-source corroboration count is {lead['source_count']}")
        if counts.get("contact_page"):
            reasons.append(f"{counts['contact_page']} contact/about page(s) checked")
        if counts.get("phone"):
            reasons.append("public phone evidence found")
        if counts.get("email"):
            reasons.append("public email evidence found")
        if counts.get("whatsapp"):
            reasons.append("public WhatsApp evidence found")
        if lead.get("enrichment_confidence") is not None:
            reasons.append(f"enrichment confidence is {lead['enrichment_confidence']}")

        return {
            "lead": lead,
            "score": score,
            "score_explanation": reasons,
            "evidence_counts": counts,
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
        age_days = (now - latest).total_seconds() / 86400 if latest else None
        fresh = bool(latest and age_days is not None and 0 <= age_days <= self.policy.evidence_fresh_days)
        source_count = int(lead.get("source_count") or 0)
        contactable = any(lead.get(k) for k in ("whatsapp", "phone", "email"))
        confidence = float(lead.get("enrichment_confidence") or 0.0)
        score = int(lead.get("score") or 0)
        tier = str(lead.get("tier") or lead.get("maha_tier") or "").lower()

        reasons: list[str] = []
        if not fresh:
            reasons.append("evidence is stale or has not been captured")
        if source_count < self.policy.min_source_count:
            reasons.append("insufficient source corroboration")
        if not contactable:
            reasons.append("no usable public contact evidence")
        if confidence < self.policy.min_enrichment_confidence:
            reasons.append("enrichment confidence is below policy threshold")
        if score < self.policy.hot_score_threshold:
            reasons.append(f"score below hot threshold ({self.policy.hot_score_threshold})")
        if tier not in {"hot", "qualified"}:
            reasons.append("lead tier is not outreach-eligible")

        needs_research = not fresh or source_count < self.policy.min_source_count or not contactable or confidence < self.policy.min_enrichment_confidence
        allowed = not reasons
        return {
            "lead_id": lead_id,
            "allowed": allowed,
            "decision": "READY_FOR_HUMAN_APPROVAL" if allowed else "RESEARCH_REQUIRED",
            "needs_research": needs_research,
            "latest_evidence_at": latest_raw,
            "evidence_age_days": round(age_days, 3) if age_days is not None else None,
            "freshness_window_days": self.policy.evidence_fresh_days,
            "reasons": reasons or ["evidence and lead quality meet outreach policy"],
        }

    def get_lead_intelligence(self, lead_id: str, now: datetime | None = None) -> dict[str, Any]:
        report = self.explain_lead(lead_id)
        return {**report, "outreach_decision": self.outreach_decision(lead_id, now=now)}
