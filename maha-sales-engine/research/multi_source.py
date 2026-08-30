from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Protocol
from urllib.parse import urlparse


class ResearchProvider(Protocol):
    name: str
    source_type: str

    def search(self, query: str, limit: int = 10, enrich: bool = True) -> list[dict[str, Any]]: ...


@dataclass(frozen=True)
class SourcePolicy:
    """Quality weights for public-source discovery."""

    domain_weights: tuple[tuple[str, float], ...] = (
        ("asitabali.org", 1.00),
        ("asita.or.id", 0.98),
        ("phribali.or.id", 0.98),
        ("bali.com", 0.80),
        ("whatsnewindonesia.com", 0.72),
    )
    default_weight: float = 0.55

    def weight_for(self, url: str | None) -> float:
        host = urlparse(url or "").netloc.casefold().split(":", 1)[0]
        for domain, weight in self.domain_weights:
            if host == domain or host.endswith("." + domain):
                return weight
        return self.default_weight


class MultiSourceResearcher:
    """Run multiple public-search providers and merge corroborating records."""

    def __init__(self, providers: list[ResearchProvider], policy: SourcePolicy | None = None) -> None:
        if not providers:
            raise ValueError("at least one research provider is required")
        self.providers = providers
        self.policy = policy or SourcePolicy()

    @staticmethod
    def _normalize_text(value: str) -> str:
        value = value.casefold()
        value = re.sub(r"[^a-z0-9]+", " ", value)
        return re.sub(r"\s+", " ", value).strip()

    @classmethod
    def _name_key(cls, value: str) -> str:
        value = cls._normalize_text(value)
        value = re.sub(r"\b(pt|cv|tb|ud|the|bali|indonesia)\b", " ", value)
        return re.sub(r"\s+", " ", value).strip()

    @staticmethod
    def _phone_key(value: str | None) -> str:
        digits = re.sub(r"\D", "", value or "")
        if digits.startswith("0"):
            digits = "62" + digits[1:]
        return digits

    @staticmethod
    def _domain_key(value: str | None) -> str:
        return urlparse(value or "").netloc.casefold().replace("www.", "")

    def _dedupe_key(self, item: dict[str, Any]) -> tuple[str, str]:
        phone = self._phone_key(item.get("phone"))
        domain = self._domain_key(item.get("website") or item.get("url"))
        name = self._name_key(str(item.get("company") or item.get("title") or ""))
        if phone:
            return ("phone", phone)
        if domain:
            return ("domain", domain)
        return ("name", name)

    def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        if not 1 <= limit <= 50:
            raise ValueError("limit must be between 1 and 50")
        merged: dict[tuple[str, str], dict[str, Any]] = {}
        for provider in self.providers:
            try:
                raw_results = provider.search(query, limit=limit, enrich=True)
            except Exception:
                continue
            for raw in raw_results:
                url = raw.get("url") or raw.get("source_url")
                title = str(raw.get("company") or raw.get("title") or "").strip()
                if not title:
                    continue
                quality = self.policy.weight_for(url)
                key = self._dedupe_key(raw)
                candidate = {
                    **raw,
                    "company": title,
                    "source": provider.name,
                    "source_type": provider.source_type,
                    "source_url": url,
                    "source_quality": quality,
                    "researched_at": datetime.now(timezone.utc).isoformat(),
                    "sources": [{
                        "provider": provider.name,
                        "source_type": provider.source_type,
                        "url": url,
                        "title": title,
                        "snippet": str(raw.get("snippet", "")),
                        "quality": quality,
                    }],
                }
                existing = merged.get(key)
                if existing is None:
                    merged[key] = candidate
                    continue
                existing_quality = float(existing.get("source_quality", 0.0))
                existing["sources"].extend(candidate["sources"])
                existing["source_quality"] = max(existing_quality, quality)
                existing["source_count"] = len(existing["sources"])
                if quality > existing_quality:
                    for field in ("phone", "email", "website", "source_url"):
                        if candidate.get(field):
                            existing[field] = candidate[field]
                    existing["source"] = provider.name
                    existing["source_type"] = provider.source_type
                for field in ("phone", "email", "website"):
                    if not existing.get(field) and candidate.get(field):
                        existing[field] = candidate[field]
                snippets = [existing.get("research_snippet", ""), str(raw.get("snippet", ""))]
                existing["research_snippet"] = " | ".join(dict.fromkeys(x for x in snippets if x)).strip()
        ranked = list(merged.values())
        for item in ranked:
            item["source_count"] = len(item.get("sources", []))
            item["research_confidence"] = min(
                1.0, float(item.get("source_quality", 0.0)) + 0.05 * max(0, item["source_count"] - 1)
            )
        ranked.sort(key=lambda x: (-float(x["research_confidence"]), -float(x["source_quality"]), self._name_key(x["company"])))
        return ranked[:limit]
