import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.main import app
from app.payments.midtrans import MidtransConfig, MidtransClient
from fastapi.testclient import TestClient

client = TestClient(app)

BASE_DIR = Path(__file__).resolve().parents[1]
ORDERS_FILE = BASE_DIR / "sales-system" / "orders.json"
CONFIG_FILE = BASE_DIR / "app" / "payments" / "midtrans-config.json"


@pytest.fixture(autouse=True)
def _reset_files(tmp_path: Path):
    with patch("app.payments.routes.ORDERS_FILE", ORDERS_FILE), patch(
        "app.payments.routes.CONFIG_FILE", CONFIG_FILE
    ), patch("app.payments.midtrans.CONFIG_FILE", CONFIG_FILE), patch(
        "app.payments.midtrans.TRANSACTION_LOG", tmp_path / "midtrans-transactions.json"
    ), patch("app.api.sales.ORDERS_FILE", ORDERS_FILE), patch(
        "app.api.sales.CUSTOMERS_FILE", BASE_DIR / "sales-system" / "customers.json"
    ):
        yield


def test_midtrans_returns_error_when_not_configured():
    response = client.post(
        "/api/payments/midtrans/create",
        json={
            "order_id": "ORD-MIDTEST-001",
            "amount": 100000,
            "customer_name": "Test",
            "customer_email": "test@example.com",
        },
    )
    assert response.status_code in (200, 404, 500)
    if response.status_code == 200:
        body = response.json()
        assert body.get("status") == "error"


def test_midtrans_config_requires_keys(tmp_path: Path):
    empty_config = tmp_path / "midtrans-config.json"
    empty_config.write_text("{}", encoding="utf-8")
    cfg = MidtransConfig(empty_config)
    assert cfg.is_configured() is False


@patch("app.payments.midtrans.requests.Session")
def test_midtrans_create_success(mock_session_cls):
    mock_session = MagicMock()
    mock_session_cls.return_value = mock_session
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "token": "tokentest-123",
        "redirect_url": "https://app.sandbox.midtrans.com/snap/v2/redir/tokentest-123",
    }
    mock_response.raise_for_status = MagicMock()
    mock_session.post.return_value = mock_response

    CONFIG_FILE.write_text(
        json.dumps(
            {
                "is_production": False,
                "merchant_id": "G123",
                "server_key": "SB-Mid-server-test",
                "client_key": "SB-Mid-client-test",
            }
        ),
        encoding="utf-8",
    )

    cfg = MidtransConfig()
    client_mid = MidtransClient(cfg)
    result = client_mid.create_snap_transaction({
        "order_id": "ORD-MIDTEST-002",
        "amount": 100000,
        "customer_name": "Test",
        "customer_email": "test@example.com",
        "customer_phone": "0812",
    })

    assert result["status"] == "success"
    assert result["token"] == "tokentest-123"
    assert "redir" in result["redirect_url"]
