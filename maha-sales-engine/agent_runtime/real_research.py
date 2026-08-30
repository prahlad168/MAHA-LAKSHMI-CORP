from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from content.engine import ContentEngine
from research.agent import ResearchAgent
from research.multi_source import SourcePolicy

from .sales_runtime_v2 import build_sales_runtime_v2


def build_default_content_engine() -> ContentEngine:
    return ContentEngine(config=None, product_manager=None)


def run_bali_research(
    limit: int = 10,
    db_path: Path | None = None,
    research_agent: ResearchAgent | None = None,
) -> Any:
    """Dynamically research, rank and queue Bali outreach for human approval."""
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    agent = research_agent or ResearchAgent(policy=SourcePolicy())
    candidates = agent.run(limit=limit)
    if not candidates:
        raise RuntimeError("multi-source research returned no candidates")
    runtime = build_sales_runtime_v2(db_path or Path("db/maha_sales_engine.db"), build_default_content_engine())
    return runtime.run(
        f"Multi-source research and prepare outreach for top {limit} Bali businesses",
        candidates,
    )
