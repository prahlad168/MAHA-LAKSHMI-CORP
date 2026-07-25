import json
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

BASE_DIR = Path(__file__).resolve().parents[1]
PRODUCTS_FILE = BASE_DIR / "sales-system" / "products.json"
ORDERS_FILE = BASE_DIR / "sales-system" / "orders.json"
CUSTOMERS_FILE = BASE_DIR / "sales-system" / "customers.json"


@pytest.fixture(autouse=True)
def _reset_sales_files(tmp_path: Path):
    with patch("app.api.sales.PRODUCTS_FILE", PRODUCTS_FILE), patch(
        "app.api.sales.ORDERS_FILE", ORDERS_FILE
    ), patch("app.api.sales.CUSTOMERS_FILE", CUSTOMERS_FILE):
        yield


def test_list_products():
    res = client.get("/api/sales/products")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(p["id"] == "whatsapp-kit" for p in data)


def test_get_product_not_found():
    res = client.get("/api/sales/products/unknown")
    assert res.status_code == 404


def test_create_order_and_list():
    payload = {
        "customer": {"name": "Test User", "email": "test@example.com", "whatsapp": "0812", "country": "ID"},
        "items": [{"product_id": "whatsapp-kit", "quantity": 1}],
        "payment_method": "bca",
        "currency": "IDR",
    }
    res = client.post("/api/sales/orders", json=payload)
    assert res.status_code == 200
    order = res.json()
    assert order["status"] == "pending"
    assert order["total"] == 250000.0
    assert order["currency"] == "IDR"
    assert "order_id" in order

    res2 = client.get("/api/sales/orders")
    assert res2.status_code == 200
    assert len(res2.json()) >= 1


def test_verify_payment():
    payload = {
        "customer": {"name": "Test", "email": "t@t.com", "whatsapp": "", "country": "ID"},
        "items": [{"product_id": "whatsapp-kit", "quantity": 1}],
        "payment_method": "bca",
        "currency": "IDR",
    }
    create = client.post("/api/sales/orders", json=payload).json()
    order_id = create["order_id"]

    res = client.post(f"/api/sales/orders/{order_id}/verify", json={"order_id": order_id, "txid": "TX123"})
    assert res.status_code == 200
    assert res.json()["status"] == "paid"


def test_daily_report():
    res = client.get("/api/sales/reports/daily")
    assert res.status_code == 200
    data = res.json()
    assert "total_revenue" in data
    assert "ceo_share_usdt" in data
    assert data["ceo_share_usdt"]["share_percent"] == 100


def test_summary_report():
    res = client.get("/api/sales/reports/summary")
    assert res.status_code == 200
    data = res.json()
    assert "total_revenue_idr" in data
    assert "ceo_share" in data
    assert data["ceo_share"]["percent"] == 100
    assert data["ceo_share"]["wallet"] == "TNFs1SP2C8HxGSZkSH3hJamf8ukgtnW7U6"


def test_transaction_history():
    res = client.get("/api/sales/reports/transactions?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert "transactions" in data
    assert "count" in data
