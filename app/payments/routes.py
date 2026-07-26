#!/usr/bin/env python3
"""
MAHA LAKSHMI AIOS - Payment Gateway Routes
Midtrans Snap integration + webhook notification.
"""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from app.payments.midtrans import MidtransClient, MidtransConfig

router = APIRouter(prefix="/api/payments", tags=["payments"])

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent.parent
ORDERS_FILE = BASE_DIR / "sales-system" / "orders.json"
CONFIG_FILE = BASE_DIR / "app" / "payments" / "midtrans-config.json"

client = MidtransClient(MidtransConfig(CONFIG_FILE))


class CreatePaymentRequest(BaseModel):
    order_id: str
    amount: int = Field(..., gt=0)
    currency: str = "IDR"
    customer_name: str
    customer_email: str
    customer_phone: str = ""
    items: list = Field(default_factory=list)
    finish_url: str = "https://mahalaksmi.web.id/products"


class VerifyPaymentRequest(BaseModel):
    order_id: str
    transaction_status: str
    gross_amount: str
    payment_type: str = ""
    fraud_status: str = ""
    transaction_time: str = ""


def _load_orders() -> Dict[str, Any]:
    if not ORDERS_FILE.exists():
        return {"orders": []}
    return json.loads(ORDERS_FILE.read_text(encoding="utf-8"))


def _save_orders(data: Dict[str, Any]) -> None:
    ORDERS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _find_order(order_id: str) -> Optional[Dict[str, Any]]:
    data = _load_orders()
    for order in data.get("orders", []):
        if order.get("order_id") == order_id:
            return order
    return None


def _update_order_status(order_id: str, **kwargs) -> None:
    data = _load_orders()
    for order in data.get("orders", []):
        if order.get("order_id") == order_id:
            order.update(kwargs)
            order["updated_at"] = datetime.now(timezone.utc).isoformat()
            break
    _save_orders(data)


@router.post("/midtrans/create")
async def create_midtrans_payment(request: CreatePaymentRequest):
    order = _find_order(request.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    items = request.items or [
        {
            "id": item.get("product_id"),
            "name": item.get("name", "Product"),
            "price": int(item.get("price", 0)),
            "quantity": item.get("quantity", 1),
        }
        for item in order.get("items", [])
    ]

    payload = {
        "order_id": request.order_id,
        "amount": request.amount,
        "customer_name": request.customer_name or order.get("customer", {}).get("name", "Customer"),
        "customer_email": request.customer_email or order.get("customer", {}).get("email", ""),
        "customer_phone": request.customer_phone or order.get("customer", {}).get("whatsapp", ""),
        "items": items,
        "finish_url": request.finish_url,
    }

    result = client.create_snap_transaction(payload)
    if result.get("status") != "success":
        raise HTTPException(status_code=400, detail=result.get("message", "Failed to create payment"))

    _update_order_status(
        request.order_id,
        status="awaiting_payment",
        midtrans_token=result.get("token"),
        midtrans_redirect_url=result.get("redirect_url"),
    )

    return {
        "order_id": request.order_id,
        "token": result.get("token"),
        "redirect_url": result.get("redirect_url"),
    }


@router.get("/midtrans/status/{order_id}")
async def get_midtrans_status(order_id: str):
    result = client.check_transaction(order_id)
    if result.get("status") != "success":
        raise HTTPException(status_code=400, detail=result.get("message", "Failed to check status"))

    transaction_status = result.get("transaction_status", "")
    if transaction_status == "settlement" or transaction_status == "capture":
        _update_order_status(
            order_id,
            status="paid",
            payment_method="midtrans",
            verified_at=datetime.now(timezone.utc).isoformat(),
            midtrans_transaction_status=transaction_status,
            midtrans_fraud_status=result.get("fraud_status"),
            midtrans_payment_type=result.get("payment_type"),
        )

    return result


@router.post("/midtrans/notification")
async def midtrans_notification(request: Request):
    body = await request.json()
    order_id = body.get("order_id", "")
    transaction_status = body.get("transaction_status", "")
    gross_amount = str(body.get("gross_amount", ""))
    fraud_status = body.get("fraud_status", "")

    if not client.verify_signature(body):
        logger.warning("Invalid Midtrans signature for order %s", order_id)
        raise HTTPException(status_code=403, detail="Invalid signature")

    status_map = {
        "capture": "paid",
        "settlement": "paid",
        "pending": "awaiting_payment",
        "deny": "failed",
        "expire": "expired",
        "cancel": "cancelled",
    }

    new_status = status_map.get(transaction_status, "pending")
    update_payload = {
        "status": new_status,
        "midtrans_transaction_status": transaction_status,
        "midtrans_fraud_status": fraud_status,
        "payment_method": "midtrans",
        "midtrans_payment_type": body.get("payment_type"),
        "verified_at": datetime.now(timezone.utc).isoformat() if new_status == "paid" else None,
        "txid": body.get("transaction_id"),
    }

    _update_order_status(order_id, **update_payload)
    _log_transaction("webhook", order_id, body)

    return {"status": "ok"}


def _log_transaction(action: str, order_id: str, data: Dict[str, Any]) -> None:
    try:
        log_file = BASE_DIR / "app" / "payments" / "midtrans-transactions.json"
        existing: Dict[str, Any] = {}
        if log_file.exists():
            existing = json.loads(log_file.read_text(encoding="utf-8"))
        log = existing.setdefault("transactions", [])
        log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "order_id": order_id,
            "data": data,
        })
        log_file.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as exc:
        logger.error("Midtrans log failed: %s", exc)
