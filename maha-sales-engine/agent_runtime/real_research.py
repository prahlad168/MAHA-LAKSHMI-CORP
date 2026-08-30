from __future__ import annotations

from pathlib import Path
from typing import Any

from content.engine import ContentEngine
from research.bali import get_bali_research_leads

from .vertical_slice import SalesRuntime, build_sales_runtime


def build_default_content_engine() -> ContentEngine:
    # WhatsApp generation only needs the template catalog; product access is deferred.
    return ContentEngine(config=None, product_manager=None)


def run_bali_research(limit: int = 10, db_path: Path | None = None) -> Any:
    """Run the real researched Bali lead seed through the durable sales runtime."""
    runtime = build_sales_runtime(db_path or Path("db/maha_sales_engine.db"), build_default_content_engine())
    candidates = get_bali_research_leads(limit)
    return runtime.run(
        request=f"Research and prepare outreach for {len(candidates)} Bali businesses",
        candidates=candidates,
    )
