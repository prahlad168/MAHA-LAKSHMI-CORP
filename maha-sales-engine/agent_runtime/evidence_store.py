from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class LeadEvidenceStore:
    """Durable enrichment-evidence store sharing the MAHA CRM database."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("""CREATE TABLE IF NOT EXISTS lead_evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id TEXT NOT NULL,
                evidence_type TEXT NOT NULL,
                source_url TEXT,
                page_url TEXT,
                value TEXT,
                confidence REAL,
                captured_at TEXT NOT NULL,
                metadata_json TEXT NOT NULL DEFAULT '{}'
            )""")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_lead_evidence_lead ON lead_evidence(lead_id, id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_lead_evidence_type ON lead_evidence(evidence_type)")

    def save(self, lead_id: str, lead: dict[str, Any]) -> int:
        now = datetime.now(timezone.utc).isoformat()
        records: list[tuple[str, str | None, str | None, str | None, float | None, dict[str, Any]]] = []
        for src in lead.get("sources", []) or []:
            records.append(("source", src.get("url"), src.get("url"), src.get("title"), src.get("quality"), {
                "provider": src.get("provider"), "source_type": src.get("source_type"), "snippet": src.get("snippet"),
            }))
        for url in lead.get("contact_pages", []) or []:
            records.append(("contact_page", lead.get("website") or lead.get("source_url"), url, url, lead.get("enrichment_confidence"), {}))
        for email in lead.get("discovered_emails", []) or []:
            records.append(("email", lead.get("website") or lead.get("source_url"), None, email, lead.get("enrichment_confidence"), {}))
        for phone in lead.get("discovered_phones", []) or []:
            records.append(("phone", lead.get("website") or lead.get("source_url"), None, phone, lead.get("enrichment_confidence"), {}))
        for url in lead.get("whatsapp_urls", []) or []:
            records.append(("whatsapp", lead.get("website") or lead.get("source_url"), None, url, lead.get("enrichment_confidence"), {}))
        for key, kind in (("research_snippet", "research_snippet"), ("research_host", "research_host")):
            if lead.get(key):
                records.append((kind, lead.get("source_url"), None, str(lead[key]), lead.get("research_confidence"), {}))
        for key, kind in (("research_confidence", "research_confidence"), ("enrichment_status", "enrichment_status"), ("enrichment_confidence", "enrichment_confidence")):
            if lead.get(key) is not None:
                records.append((kind, lead.get("website") or lead.get("source_url"), None, str(lead[key]), lead.get("enrichment_confidence", lead.get("research_confidence")), {}))

        inserted = 0
        with sqlite3.connect(self.db_path) as conn:
            for kind, source_url, page_url, value, confidence, metadata in records:
                exists = conn.execute(
                    "SELECT 1 FROM lead_evidence WHERE lead_id=? AND evidence_type=? AND COALESCE(source_url,'')=COALESCE(?,'') AND COALESCE(page_url,'')=COALESCE(?,'') AND COALESCE(value,'')=COALESCE(?,'') LIMIT 1",
                    (lead_id, kind, source_url, page_url, value),
                ).fetchone()
                if exists:
                    continue
                conn.execute(
                    "INSERT INTO lead_evidence(lead_id,evidence_type,source_url,page_url,value,confidence,captured_at,metadata_json) VALUES (?,?,?,?,?,?,?,?)",
                    (lead_id, kind, source_url, page_url, value, confidence, now, json.dumps(metadata, ensure_ascii=False, default=str)),
                )
                inserted += 1
        return inserted

    def list_for_lead(self, lead_id: str) -> list[dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM lead_evidence WHERE lead_id=? ORDER BY id", (lead_id,)).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["metadata"] = json.loads(item.pop("metadata_json"))
            result.append(item)
        return result
