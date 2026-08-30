from __future__ import annotations

import re
from html import unescape
from typing import Any
from urllib.parse import quote_plus, urlparse

import requests


class WebResearchError(RuntimeError):
    pass


class DuckDuckGoResearchProvider:
    """Lightweight public-web research provider using DuckDuckGo HTML results.

    This intentionally returns research candidates only. It does not claim that a
    listing is an official contact channel; outreach must re-verify the target.
    """

    endpoint = "https://html.duckduckgo.com/html/"

    def __init__(self, timeout: float = 15.0, user_agent: str = "MAHA-Research/1.0") -> None:
        self.timeout = timeout
        self.headers = {"User-Agent": user_agent}

    @staticmethod
    def _strip_html(value: str) -> str:
        value = re.sub(r"<[^>]+>", " ", value)
        return re.sub(r"\s+", " ", unescape(value)).strip()

    def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        if not query.strip():
            raise ValueError("query must not be empty")
        if not 1 <= limit <= 50:
            raise ValueError("limit must be between 1 and 50")
        try:
            response = requests.get(
                self.endpoint,
                params={"q": query},
                headers=self.headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise WebResearchError(f"web search failed: {exc}") from exc

        html = response.text
        blocks = re.split(r'<div[^>]+class="result[^>]*>', html, flags=re.I)
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
            results.append({"title": title, "url": url, "snippet": snippet, "query": query})
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
            host = urlparse(url).netloc
            key = (result["title"] + "|" + url).casefold()
            if key in seen:
                continue
            seen.add(key)
            candidates.append({
                "company": result["title"],
                "industry": category,
                "country": "Indonesia",
                "source": "web_search",
                "source_url": url,
                "website": url,
                "research_snippet": result["snippet"],
                "research_host": host,
            })
            if len(candidates) >= limit:
                return candidates
    return candidates
