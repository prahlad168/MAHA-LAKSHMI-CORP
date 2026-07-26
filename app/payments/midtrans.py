#!/usr/bin/env python3
"""
MAHA LAKSHMI AIOS - Midtrans Payment Gateway Integration
Supports: Snap (hosted payment page), Core API (direct charge)
Docs: https://docs.midtrans.com
"""
import hashlib
import hmac
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent.parent
CONFIG_FILE = BASE_DIR / "app" / "payments" / "midtrans-config.json"
TRANSACTION_LOG = BASE_DIR / "app" / "payments" / "midtrans-transactions.json"


class MidtransConfig:
    def __init__(self, config_path: Optional[Path] = None):
        path = config_path or CONFIG_FILE
        self.config: Dict[str, Any] = {}
        if path.exists():
            self.config = json.loads(path.read_text(encoding="utf-8"))

    @property
    def server_key(self) -> str:
        return self.config.get("server_key", "")

    @property
    def client_key(self) -> str:
        return self.config.get("client_key", "")

    @property
    def merchant_id(self) -> str:
        return self.config.get("merchant_id", "")

    @property
    def is_production(self) -> bool:
        return bool(self.config.get("is_production", False))

    @property
    def base_url(self) -> str:
        if self.is_production:
            return "https://api.midtrans.com"
        return "https://api.sandbox.midtrans.com"

    @property
    def snap_url(self) -> str:
        if self.is_production:
            return "https://app.midtrans.com/snap/v1/transactions"
        return "https://app.sandbox.midtrans.com/snap/v1/transactions"

    def is_configured(self) -> bool:
        return bool(self.server_key and self.client_key and self.merchant_id)


class MidtransClient:
    def __init__(self, config: Optional[MidtransConfig] = None):
        self.config = config or MidtransConfig()
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def _auth(self) -> tuple:
        return (self.config.server_key, "")

    def create_snap_transaction(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self.config.is_configured():
            return {
                "status": "error",
                "message": "Midtrans belum dikonfigurasi. Set server_key, client_key, dan merchant_id di app/payments/midtrans-config.json",
                "token": None,
                "redirect_url": None,
            }

        url = self.config.snap_url
        auth = self._auth()
        order_id = payload.get("order_id") or f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        gross_amount = int(payload.get("amount", 0))

        body = {
            "transaction_details": {
                "order_id": order_id,
                "gross_amount": gross_amount,
            },
            "customer_details": {
                "first_name": payload.get("customer_name", "Customer"),
                "last_name": "",
                "email": payload.get("customer_email", ""),
                "phone": payload.get("customer_phone", ""),
            },
            "item_details": payload.get("items", []),
            "callbacks": {
                "finish": payload.get("finish_url", "https://mahalaksmi.web.id/products"),
                "error": payload.get("finish_url", "https://mahalaksmi.web.id/products"),
                "cancel": payload.get("finish_url", "https://mahalaksmi.web.id/products"),
            },
        }

        try:
            response = self.session.post(url, auth=auth, json=body, timeout=15)
            response.raise_for_status()
            data = response.json()
            _log_transaction("create_snap", order_id, data)
            return {
                "status": "success",
                "token": data.get("token"),
                "redirect_url": data.get("redirect_url"),
                "order_id": order_id,
            }
        except requests.RequestException as exc:
            _log_transaction("create_snap", order_id, {"error": str(exc)})
            return {
                "status": "error",
                "message": str(exc),
                "token": None,
                "redirect_url": None,
            }

    def check_transaction(self, order_id: str) -> Dict[str, Any]:
        if not self.config.is_configured():
            return {"status": "error", "message": "Midtrans belum dikonfigurasi"}

        url = f"{self.config.base_url}/v2/{order_id}/status"
        auth = self._auth()
        try:
            response = self.session.get(url, auth=auth, timeout=15)
            response.raise_for_status()
            data = response.json()
            _log_transaction("check", order_id, data)
            return {
                "status": "success",
                "transaction_status": data.get("transaction_status"),
                "gross_amount": data.get("gross_amount"),
                "payment_type": data.get("payment_type"),
                "fraud_status": data.get("fraud_status"),
                "transaction_time": data.get("transaction_time"),
            }
        except requests.RequestException as exc:
            return {"status": "error", "message": str(exc)}

    def cancel_transaction(self, order_id: str) -> Dict[str, Any]:
        if not self.config.is_configured():
            return {"status": "error", "message": "Midtrans belum dikonfigurasi"}

        url = f"{self.config.base_url}/v2/{order_id}/cancel"
        auth = self._auth()
        try:
            response = self.session.post(url, auth=auth, timeout=15)
            response.raise_for_status()
            data = response.json()
            _log_transaction("cancel", order_id, data)
            return {"status": "success", "data": data}
        except requests.RequestException as exc:
            return {"status": "error", "message": str(exc)}

    def verify_signature(self, payload: Dict[str, Any]) -> bool:
        if not self.config.is_configured():
            return False
        signature = payload.get("signature_key", "")
        expected = _build_signature(
            order_id=payload.get("order_id", ""),
            status=payload.get("transaction_status", ""),
            amount=str(payload.get("gross_amount", "")),
            server_key=self.config.server_key,
        )
        return signature == expected


def _build_signature(order_id: str, status: str, amount: str, server_key: str) -> str:
    raw = f"{order_id}|{status}|{amount}|{server_key}"
    return hashlib.sha512(raw.encode("utf-8")).hexdigest()


def _log_transaction(action: str, order_id: str, data: Dict[str, Any]) -> None:
    try:
        existing: Dict[str, Any] = {}
        if TRANSACTION_LOG.exists():
            existing = json.loads(TRANSACTION_LOG.read_text(encoding="utf-8"))
        log = existing.setdefault("transactions", [])
        log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "order_id": order_id,
            "data": data,
        })
        TRANSACTION_LOG.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as exc:
        logger.error("Midtrans log failed: %s", exc)
