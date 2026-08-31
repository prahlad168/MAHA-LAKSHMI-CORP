"""Controlled HTTP adapter for the MAHA dynamic research pipeline."""

from __future__ import annotations

import hmac
import os
import sys
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

# The sales engine is a sibling directory whose name contains a hyphen, so it
# must be placed on sys.path before importing its Python packages.
_ENGINE_ROOT = Path(__file__).resolve().parents[2] / "maha-sales-engine"
if str(_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(_ENGINE_ROOT))

from agent_runtime.real_research import run_bali_research  # noqa: E402

router = APIRouter()


class BaliResearchRequest(BaseModel):
    limit: int = Field(default=3, ge=1, le=50)


def _research_enabled() -> bool:
    return os.getenv("MAHA_RESEARCH_API_ENABLED", "false").strip().lower() == "true"


def _check_key(provided_key: str | None) -> None:
    expected_key = os.getenv("MAHA_RESEARCH_API_KEY", "")
    if not _research_enabled():
        raise HTTPException(status_code=404, detail="Research API is disabled")
    if not expected_key or not provided_key or not hmac.compare_digest(provided_key, expected_key):
        raise HTTPException(status_code=401, detail="Invalid research API key")


@router.post("/bali", tags=["Research"])
def run_bali_research_api(
    payload: BaliResearchRequest,
    x_maha_research_key: str | None = Header(default=None),
) -> dict[str, Any]:
    """Run dynamic Bali research and persist CRM/evidence/approval state."""
    _check_key(x_maha_research_key)
    try:
        result = run_bali_research(limit=payload.limit)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Research pipeline failed: {exc}") from exc

    return {
        "status": "completed",
        "pipeline": "ResearchAgentV2 -> CRM -> evidence -> Hot Leads -> sales approvals",
        "result": result,
    }
