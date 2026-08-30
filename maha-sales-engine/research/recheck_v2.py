from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

from agent_runtime.crm import CRM
from agent_runtime.evidence_store import LeadEvidenceStore
from agent_runtime.intelligence import CRMIntelligence, IntelligencePolicy
from agent_runtime.qualification import qualify_lead
from agent_runtime.store import AgentStore

from .agent_v2 import SOURCE_QUERIES, ResearchAgentV2
from .multi_source import SourcePolicy
from .ranking import rank_maha_hot_leads


@dataclass(frozen=True)
class RecheckPolicy:
    max_leads: int = 50
    evidence_fresh_days: int = 7
    min_source_count: int = 1
    min_enrichment_confidence: float = 0.45


class ResearchRecheckAgentV2:
    """Refresh only CRM leads whose research evidence is stale/incomplete."""

    def __init__(self, db_path, research_agent: ResearchAgentV2 | None = None, policy: RecheckPolicy | None = None):
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

    def queue_required(self, limit: int | None = None, now: datetime | None = None) -> list[str]:
        now = now or datetime.now(timezone.utc)
        cap = min(limit or self.policy.max_leads, self.policy.max_leads)
        ids: list[str] = []
        for lead in self._all_leads(cap * 2):
            decision = self.intelligence.outreach_decision(lead["id"], now=now)
            if decision["needs_research"] and lead.get("status") not in {"won", "lost", "do_not_contact"}:
                self.crm.set_status(lead["id"], "research_required")
                ids.append(lead["id"])
            elif not decision["needs_research"] and lead.get("status") == "research_required":
                self.crm.set_status(lead["id"], "qualified")
            if len(ids) >= cap:
                break
        return ids

    @staticmethod
    def _same_business(existing: dict[str, Any], candidate: dict[str, Any]) -> bool:
        left_domain = urlparse(str(existing.get("website") or "")).netloc.casefold().replace("www.", "")
        right_domain = urlparse(str(candidate.get("website") or candidate.get("source_url") or "")).netloc.casefold().replace("www.", "")
        if left_domain and right_domain and left_domain == right_domain:
            return True
        left = " ".join(str(existing.get("company", "")).casefold().split())
        right = " ".join(str(candidate.get("company", "")).casefold().split())
        return left == right

    def _targeted_refresh(self, lead: dict[str, Any]) -> dict[str, Any] | None:
        company = lead["company"]
        industry = str(lead.get("industry") or "business")
        base_queries = SOURCE_QUERIES.get(industry, ())
        queries = tuple(dict.fromkeys((f'"{company}" Bali Indonesia', *base_queries)))
        for provider in self.research_agent.providers:
            for query in queries:
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
        if lead.get("website"):
            return self.research_agent.enricher.enrich({**lead, "researched_at": datetime.now(timezone.utc).isoformat()})
        return None

    def recheck_lead(self, lead: dict[str, Any], now: datetime | None = None) -> dict[str, Any]:
        now = now or datetime.now(timezone.utc)
        needed, decision = self._needs_research(lead, now)
        if not needed:
            return {"lead_id": lead["id"], "status": "skipped", "decision": decision}
        refreshed = self._targeted_refresh(lead)
        if refreshed is None:
            self.crm.set_status(lead["id"], "research_required")
            return {"lead_id": lead["id"], "status": "research_failed", "decision": "RESEARCH_REQUIRED"}

        refreshed = rank_maha_hot_leads([qualify_lead(refreshed)], limit=1)[0]
        refreshed["id"] = lead["id"]
        # Never replace CRM lifecycle/follow-up state as a side effect of research.
        refreshed["status"] = "researched"
        refreshed["follow_up_state"] = lead.get("follow_up_state", "not_started")
        persisted = self.store.upsert_lead(refreshed)
        evidence_added = self.evidence.save(lead["id"], refreshed)
        after = self.intelligence.get_lead_intelligence(lead["id"], now=now)
        if after["outreach_decision"]["allowed"]:
            self.crm.set_status(lead["id"], "qualified")
            result_status = "hot_ready"
        else:
            self.crm.set_status(lead["id"], "research_required")
            result_status = "research_required"
        return {
            "lead_id": lead["id"],
            "status": result_status,
            "evidence_added": evidence_added,
            "maha_hot_score": persisted.get("score"),
            "tier": persisted.get("tier"),
            "intelligence": after,
        }

    def _needs_research(self, lead: dict[str, Any], now: datetime) -> tuple[bool, dict[str, Any]]:
        decision = self.intelligence.outreach_decision(lead["id"], now=now)
        return bool(decision["needs_research"]), decision

    def recheck_required(self, limit: int | None = None, now: datetime | None = None) -> list[dict[str, Any]]:
        now = now or datetime.now(timezone.utc)
        cap = min(limit or self.policy.max_leads, self.policy.max_leads)
        ids = self.queue_required(cap, now=now)
        leads = self._get_by_ids(ids)
        return [self.recheck_lead(lead, now=now) for lead in leads]

    def _get_by_ids(self, ids: list[str]) -> list[dict[str, Any]]:
        if not ids:
            return []
        with sqlite3.connect(self.store.db_path) as conn:
            conn.row_factory = sqlite3.Row
            placeholders = ",".join("?" for _ in ids)
            rows = conn.execute(f"SELECT * FROM crm_leads WHERE id IN ({placeholders}) ORDER BY score DESC, updated_at ASC", ids).fetchall()
        return [dict(row) for row in rows]

    def _all_leads(self, limit: int) -> list[dict[str, Any]]:
        with sqlite3.connect(self.store.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM crm_leads ORDER BY score DESC, updated_at ASC LIMIT ?", (limit,)).fetchall()
        return [dict(row) for row in rows]
