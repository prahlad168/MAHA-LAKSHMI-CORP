from __future__ import annotations

import re
from html import unescape
from typing import Any
from urllib.parse import urlparse

import requests


class WebResearchError(RuntimeError):
    pass


class DuckDuckGoResearchProvider:
    """Lightweight public-web research provider using DuckDuckGo HTML results."""

    endpoint = "https://html.duckduckgo.com/html/"

    def __init__(self, timeout: float = 15.0, user_agent: str = "MAHA-Research/1.0") -> None:
        self.timeout = timeout
        self.headers = {"User-Agent": user_agent}

    @staticmethod
    def _strip_html(value: str) -> str:
        value = re.sub(r"<[^>]+>", " ", value)
        return re.sub(r"\s+", " ", unescape(value)).strip()

    @staticmethod
    def _extract_contacts(html: str) -> tuple[str | None, str | None]:
        emails = re.findall(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", html, flags=re.I)
        phones = re.findall(r"(?:\+?62|0)(?:[\s().-]*\d){8,13}", html)
        email = next((e for e in emails if not e.lower().endswith((".png", ".jpg"))), None)
        phone = phones[0] if phones else None
        return email, phone

    def _enrich(self, url: str) -> tuple[str | None, str | None]:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return None, None
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return self._extract_contacts(response.text)
        except requests.RequestException:
            return None, None

    def search(self, query: str, limit: int = 10, enrich: bool = True) -> list[dict[str, Any]]:
        if not query.strip():
            raise ValueError("query must not be empty")
        if not 1 <= limit <= 50:
            raise ValueError("limit must be between 1 and 50")
        try:
            response = requests.get(self.endpoint, params={"q": query}, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise WebResearchError(f"web search failed: {exc}") from exc

        blocks = re.split(r'<div[^>]+class="result[^>]*>', response.text, flags=re.I)
        results: list[dict[str, Any]] = []
        for block in blocks[1:]:
            link_match = re.search(r'class="result__a"[^>]+href="([^"]+)"', block, flags=re.I)
            if not link_match:
                continue
            title_match = re.search(r'class="result__a"[^>]*>(.*?)</a>', block, flags=re.I | re.S)
            snippet_match = re.search(r'class="result__snippet"[^>]*>(.*?)</(?:a|div)>', block, flags=re.I | re.S)
            url = unescape(link_match.group(1))
            title = self._strip_html(title_match.group(1)) if title_match else ""
            snippet = self._strip_html(snippet_match.group(1)) if snippet_match else ""
            if not title or not url:
                continue
            email, phone = self._enrich(url) if enrich else (None, None)
            results.append({"title": title, "url": url, "snippet": snippet, "query": query, "email": email, "phone": phone})
            if len(results) >= limit:
                break
        return results


def discover_bali_businesses(
    limit: int = 10,
    categories: tuple[str, ...] = ("restaurant", "cafe", "hotel", "tour operator"),
    provider: DuckDuckGoResearchProvider | None = None,
) -> list[dict[str, Any]]:
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    provider = provider or DuckDuckGoResearchProvider()
    per_query = max(3, min(10, (limit + len(categories) - 1) // len(categories) + 2))
    candidates: list[dict[str, Any]] = []
    seen: set[str] = set()
    for category in categories:
        query = f"{category} Bali Indonesia business"
        for result in provider.search(query, per_query):
            url = result["url"]
            key = (result["title"] + "|" + url).casefold()
            if key in seen:
                continue
            seen.add(key)
            candidates.append({
                "company": result["title"], "industry": category, "country": "Indonesia",
                "source": "web_search", "source_url": url, "website": url,
                "email": result.get("email"), "phone": result.get("phone"),
                "research_snippet": result["snippet"], "research_host": urlparse(url).netloc,
            })
            if len(candidates) >= limit:
                return candidates
    return candidates
