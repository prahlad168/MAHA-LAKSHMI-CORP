from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from content.engine import ContentEngine
from research.web_search import DuckDuckGoResearchProvider, discover_bali_businesses

from .sales_runtime_v2 import SalesRuntimeV2, build_sales_runtime_v2


def build_default_content_engine() -> ContentEngine:
    return ContentEngine(config=None, product_manager=None)


def run_bali_research(
    limit: int = 10,
    db_path: Path | None = None,
    query_provider: DuckDuckGoResearchProvider | None = None,
) -> Any:
    """Dynamically research Bali businesses and queue non-sending outreach for approval."""
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    provider = query_provider or DuckDuckGoResearchProvider(timeout=float(os.getenv("MAHA_RESEARCH_TIMEOUT", "15")))
    candidates = discover_bali_businesses(limit=limit, provider=provider)
    if not candidates:
        raise RuntimeError("dynamic research returned no business candidates")
    runtime = build_sales_runtime_v2(db_path or Path("db/maha_sales_engine.db"), build_default_content_engine())
    return runtime.run(f"Dynamically research and prepare outreach for up to {limit} Bali businesses", candidates)
