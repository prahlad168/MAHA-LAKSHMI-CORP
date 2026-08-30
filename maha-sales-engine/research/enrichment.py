from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin, urlparse

import requests


EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
PHONE_RE = re.compile(r"(?<!\d)(?:\+?62|0)(?:[\s().-]*\d){8,13}(?!\d)")
WA_RE = re.compile(r"https?://(?:wa\.me|api\.whatsapp\.com|chat\.whatsapp\.com)/[^\"'<>\s]+", re.I)


@dataclass(frozen=True)
class EnrichmentConfig:
    timeout: float = 10.0
    max_pages: int = 4
    max_bytes: int = 1_500_000


class WebsiteEnricher:
    """Conservative public-site enrichment for business leads."""

    PATH_HINTS = ("contact", "about", "kontak", "tentang", "reserv", "booking")

    def __init__(self, config: EnrichmentConfig | None = None) -> None:
        self.config = config or EnrichmentConfig()
        self.headers = {"User-Agent": "MAHA-Research/1.0 (+public-site-enrichment)"}

    @staticmethod
    def _normalize_phone(value: str | None) -> str | None:
        if not value:
            return None
        digits = re.sub(r"\D", "", value)
        if digits.startswith("0"):
            digits = "62" + digits[1:]
        if not digits.startswith("62") or not 9 <= len(digits) <= 15:
            return None
        return "+" + digits

    @staticmethod
    def _links(html: str, base_url: str) -> list[str]:
        hrefs = re.findall(r"href=[\"']([^\"']+)[\"']", html, re.I)
        return [urljoin(base_url, href) for href in hrefs]

    def _fetch(self, url: str) -> tuple[str, str] | None:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            return None
        try:
            response = requests.get(url, headers=self.headers, timeout=self.config.timeout)
            response.raise_for_status()
            content = response.content[: self.config.max_bytes]
            encoding = response.encoding or "utf-8"
            return content.decode(encoding, errors="ignore"), response.url
        except requests.RequestException:
            return None

    @staticmethod
    def _unique_phones(values: list[str]) -> list[str]:
        normalized = [WebsiteEnricher._normalize_phone(value) for value in values]
        normalized = [value for value in normalized if value]
        result: list[str] = []
        for candidate in sorted(set(normalized), key=len, reverse=True):
            if any(candidate.startswith(existing) or existing.startswith(candidate) for existing in result):
                continue
            result.append(candidate)
        return result

    def enrich(self, lead: dict[str, Any]) -> dict[str, Any]:
        website = str(lead.get("website") or lead.get("source_url") or "").strip()
        if not website:
            return {**lead, "enrichment_status": "no_website", "enrichment_confidence": 0.0}

        first = self._fetch(website)
        if first is None:
            return {**lead, "enrichment_status": "unreachable", "enrichment_confidence": 0.0}

        html, final_url = first
        pages = [(final_url, html)]
        base_host = urlparse(final_url).netloc.casefold()
        candidates = []
        for link in self._links(html, final_url):
            parsed = urlparse(link)
            if parsed.netloc.casefold() != base_host:
                continue
            path = parsed.path.casefold()
            if any(hint in path for hint in self.PATH_HINTS):
                candidates.append(link)
        for link in candidates[: max(0, self.config.max_pages - 1)]:
            fetched = self._fetch(link)
            if fetched:
                pages.append(fetched)

        emails: list[str] = []
        phones: list[str] = []
        whatsapp_urls: list[str] = []
        contact_pages: list[str] = []
        for url, body in pages:
            emails.extend(EMAIL_RE.findall(body))
            phones.extend(PHONE_RE.findall(body))
            whatsapp_urls.extend(WA_RE.findall(body))
            if any(hint in urlparse(url).path.casefold() for hint in self.PATH_HINTS):
                contact_pages.append(url)

        normalized_phones = self._unique_phones(phones)
        emails = list(dict.fromkeys(e.lower() for e in emails))
        whatsapp_urls = list(dict.fromkeys(whatsapp_urls))
        score = 0.35
        score += 0.20 if emails else 0
        score += 0.20 if normalized_phones else 0
        score += 0.15 if whatsapp_urls else 0
        score += 0.10 if contact_pages else 0

        result = {
            **lead,
            "website": final_url,
            "email": lead.get("email") or (emails[0] if emails else None),
            "phone": lead.get("phone") or (normalized_phones[0] if normalized_phones else None),
            "whatsapp": lead.get("whatsapp") or (whatsapp_urls[0] if whatsapp_urls else None),
            "contact_pages": list(dict.fromkeys(contact_pages)),
            "discovered_emails": emails,
            "discovered_phones": normalized_phones,
            "whatsapp_urls": whatsapp_urls,
            "enrichment_status": "enriched",
            "enrichment_confidence": min(1.0, round(score, 2)),
        }
        return result


def enrich_leads(leads: list[dict[str, Any]], enricher: WebsiteEnricher | None = None) -> list[dict[str, Any]]:
    enricher = enricher or WebsiteEnricher()
    return [enricher.enrich(lead) for lead in leads]
