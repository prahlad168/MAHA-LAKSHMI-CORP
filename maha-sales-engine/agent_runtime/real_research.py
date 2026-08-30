from __future__ import annotations

from pathlib import Path
from typing import Any

from content.engine import ContentEngine
from research.agent_v2 import ResearchAgentV2
from research.multi_source import SourcePolicy

from .sales_runtime_v3 import build_sales_runtime_v3


def build_default_content_engine() -> ContentEngine:
    return ContentEngine(config=None, product_manager=None)


def run_bali_research(
    limit: int = 10,
    db_path: Path | None = None,
    research_agent: ResearchAgentV2 | None = None,
) -> Any:
    """Dynamic ResearchAgentV2 -> CRM evidence -> Hot Leads -> Sales approvals."""
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    agent = research_agent or ResearchAgentV2(policy=SourcePolicy())
    candidates = agent.run(limit=limit, enrich=True)
    if not candidates:
        raise RuntimeError("ResearchAgentV2 returned no candidates")
    runtime = build_sales_runtime_v3(
        db_path or Path("db/maha_sales_engine.db"),
        build_default_content_engine(),
    )
    return runtime.run(
        f"ResearchAgentV2 and prepare outreach for top {limit} Bali businesses",
        candidates,
    )
