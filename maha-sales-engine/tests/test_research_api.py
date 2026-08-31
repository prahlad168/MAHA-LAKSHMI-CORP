from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

# Tests run with maha-sales-engine as cwd; add repository root for backend imports.
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.main import app  # noqa: E402


def test_research_endpoint_is_disabled_by_default(monkeypatch):
    monkeypatch.delenv("MAHA_RESEARCH_API_ENABLED", raising=False)
    monkeypatch.delenv("MAHA_RESEARCH_API_KEY", raising=False)
    client = TestClient(app)

    response = client.post("/api/research/bali", json={"limit": 1})

    assert response.status_code == 404
    assert response.json()["error"] == "Research API is disabled"


def test_research_endpoint_rejects_invalid_key(monkeypatch):
    monkeypatch.setenv("MAHA_RESEARCH_API_ENABLED", "true")
    monkeypatch.setenv("MAHA_RESEARCH_API_KEY", "test-secret")
    client = TestClient(app)

    response = client.post(
        "/api/research/bali",
        json={"limit": 1},
        headers={"X-MAHA-Research-Key": "wrong"},
    )

    assert response.status_code == 401
    assert response.json()["error"] == "Invalid research API key"


def test_research_endpoint_runs_pipeline_with_valid_key(monkeypatch):
    monkeypatch.setenv("MAHA_RESEARCH_API_ENABLED", "true")
    monkeypatch.setenv("MAHA_RESEARCH_API_KEY", "test-secret")

    import backend.research.routes as research_routes

    monkeypatch.setattr(
        research_routes,
        "run_bali_research",
        lambda limit: {"lead_count": limit, "approval_queue": 1},
    )
    client = TestClient(app)

    response = client.post(
        "/api/research/bali",
        json={"limit": 1},
        headers={"X-MAHA-Research-Key": "test-secret"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "completed"
    assert payload["result"] == {"lead_count": 1, "approval_queue": 1}
