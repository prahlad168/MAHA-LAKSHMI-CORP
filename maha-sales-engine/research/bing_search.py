from __future__ import annotations

import re
from html import unescape
from typing import Any
from urllib.parse import urlparse

import requests

from .web_search import WebResearchError


class BingResearchProvider:
    """Public web-search provider using Bing HTML search results."""

    name = "bing"
    source_type = "search_engine"
    endpoint = "https://www.bing.com/search"

    def __init__(self, timeout: float = 15.0, user_agent: str = "MAHA-Research/1.0") -> None:
        self.timeout = timeout
        self.headers = {"User-Agent": user_agent}

    @staticmethod
    def _strip_html(value: str) -> str:
        return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value))).strip()

    def search(self, query: str, limit: int = 10, enrich: bool = False) -> list[dict[str, Any]]:
        if not query.strip():
            raise ValueError("query must not be empty")
        if not 1 <= limit <= 50:
            raise ValueError("limit must be between 1 and 50")
        try:
            response = requests.get(
                self.endpoint,
                params={"q": query, "count": limit},
                headers=self.headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise WebResearchError(f"Bing search failed: {exc}") from exc

        results: list[dict[str, Any]] = []
        blocks = re.findall(r'<li[^>]+class="b_algo"[^>]*>(.*?)</li>', response.text, flags=re.I | re.S)
        for block in blocks:
            link = re.search(r'<h2[^>]*>\s*<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', block, flags=re.I | re.S)
            if not link:
                continue
            snippet = re.search(r'<p[^>]*>(.*?)</p>', block, flags=re.I | re.S)
            url = unescape(link.group(1))
            title = self._strip_html(link.group(2))
            if not urlparse(url).scheme or not title:
                continue
            results.append({
                "title": title,
                "url": url,
                "snippet": self._strip_html(snippet.group(1)) if snippet else "",
                "query": query,
            })
            if len(results) >= limit:
                break
        return results
