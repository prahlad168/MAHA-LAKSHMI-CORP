from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

from agent_runtime.crm import CRM
from agent_runtime.evidence_store import LeadEvidenceStore
from agent_runtime.intelligence import CRMIntelligence, IntelligencePolicy
from agent_runtime.store import AgentStore

from .agent_v2 import SOURCE_QUERIES, ResearchAgentV2
from .multi_source import SourcePolicy


@dataclass(frozen=True)
class RecheckPolicy:
    max_leads: int = 50
    evidence_fresh_days: int = 7
    min_source_count: int = 1
    min_enrichment_confidence: float = 0.45


class ResearchRecheckAgent:
    """Targeted re-research for leads whose evidence is stale or incomplete.

    The agent never creates a new CRM identity intentionally: it updates the
    existing lead by its stable CRM id and appends fresh evidence.
    """

    def __init__(
        self,
        db_path,
        research_agent: ResearchAgentV2 | None = None,
        policy: RecheckPolicy | None = None,
    ) -> None:
        self.store = AgentStore(db_path)
        self.evidence = LeadEvidenceStore(db_path)
        self.crm = CRM(db_path)
        self.policy = policy or RecheckPolicy()
        self.intelligence = CRMIntelligence(
            self.store,
            self.evidence,
            IntelligencePolicy(
                evidence_fresh_days=self.policy.evidence_fresh_days,
                min_source_count=self.policy.min_source_count,
                min_enrichment_confidence=self.policy.min_enrichment_confidence,
            ),
        )
        self.research_agent = research_agent or ResearchAgentV2(policy=SourcePolicy())

    def _needs_research(self, lead: dict[str, Any], now: datetime) -> tuple[bool, dict[str, Any]]:
        decision = self.intelligence.outreach_decision(lead["id"], now=now)
        return bool(decision["needs_research"]), decision

    @staticmethod
    def _same_business(existing: dict[str, Any], candidate: dict[str, Any]) -> bool:
        existing_domain = urlparse(str(existing.get("website") or "")).netloc.casefold().replace("www.", "")
        candidate_domain = urlparse(str(candidate.get("website") or candidate.get("source_url") or "")).netloc.casefold().replace("www.", "")
        if existing_domain and candidate_domain and existing_domain == candidate_domain:
            return True
        left = " ".join(str(existing.get("company", "")).casefold().split())
        right = " ".join(str(candidate.get("company", "")).casefold().split())
        return left == right

    def _candidate_for(self, lead: dict[str, Any]) -> dict[str, Any] | None:
        company = lead["company"]
        industry = str(lead.get("industry") or "business")
        queries = SOURCE_QUERIES.get(industry, (f"{company} Bali Indonesia",))
        for query in queries:
            for provider in self.research_agent.providers:
                try:
                    results = provider.search(query, limit=8, enrich=True)
                except Exception:
                    continue
                for result in results:
                    candidate = {
                        **result,
                        "company": str(result.get("company") or result.get("title") or "").strip(),
                        "website": result.get("website") or result.get("url"),
                        "source_url": result.get("source_url") or result.get("url"),
                        "source": result.get("source") or provider.name,
                        "industry": industry,
                        "country": lead.get("country", "Indonesia"),
                        "language": lead.get("language", "id"),
                        "researched_at": datetime.now(timezone.utc).isoformat(),
                    }
                    if self._same_business(lead, candidate):
                        return self.research_agent.enricher.enrich({**lead, **candidate})
        # If discovery fails, re-enrich the existing official website only.
        if lead.get("website"):
            return self.research_agent.enricher.enrich({**lead, "researched_at": datetime.now(timezone.utc).isoformat()})
        return None

    def recheck_lead(self, lead: dict[str, Any], now: datetime | None = None) -> dict[str, Any]:
        now = now or datetime.now(timezone.utc)
        needed, before = self._needs_research(lead, now)
        if not needed:
            return {"lead_id": lead["id"], "status": "skipped", "decision": before}

        refreshed = self._candidate_for(lead)
        if refreshed is None:
            self.crm.set_status(lead["id"], "nurture")
            return {
                "lead_id": lead["id"],
                "status": "research_failed",
                "decision": "RESEARCH_REQUIRED",
                "reason": "targeted recheck found no matching public source",
            }

        refreshed["id"] = lead["id"]
        # Preserve CRM lifecycle and follow-up state during a research refresh.
        refreshed["status"] = lead.get("status") if lead.get("status") not in {"new", "researched"} else "researched"
        refreshed["follow_up_state"] = lead.get("follow_up_state", "not_started")
        persisted = self.store.upsert_lead(refreshed)
        evidence_count = self.evidence.save(lead["id"], refreshed)

        after = self.intelligence.get_lead_intelligence(lead["id"], now=now)
        if after["outreach_decision"]["allowed"]:
            self.crm.set_status(lead["id"], "qualified")
            final_status = "hot_ready"
        else:
            final_status = "research_required"
        return {
            "lead_id": lead["id"],
            "status": final_status,
            "evidence_added": evidence_count,
            "maha_hot_score": persisted.get("score"),
            "tier": persisted.get("tier"),
            "intelligence": after,
        }

    def recheck_required(self, limit: int | None = None, now: datetime | None = None) -> list[dict[str, Any]]:
        now = now or datetime.now(timezone.utc)
        max_leads = min(limit or self.policy.max_leads, self.policy.max_leads)
        leads = self._all_leads(max_leads)
        results = []
        for lead in leads:
            needed, _ = self._needs_research(lead, now)
            if needed:
                results.append(self.recheck_lead(lead, now=now))
        return results

    def _all_leads(self, limit: int) -> list[dict[str, Any]]:
        import sqlite3
        with sqlite3.connect(self.store.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM crm_leads ORDER BY score DESC, updated_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(row) for row in rows]
