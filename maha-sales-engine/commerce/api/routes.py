#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Commerce REST API
REST endpoints for commerce operations.
"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from core.engine import ConfigManager, DatabaseManager
from core.engine import CommerceCore
from orders.engine import OrderEngine
from payments.sdk import PaymentRequest
from licenses.engine import LicenseEngine
from subscriptions.engine import SubscriptionEngine
from delivery.engine import DigitalDeliveryEngine
from invoices.engine import InvoiceEngine
from coupons.engine import CouponEngine
from promotions.engine import PromotionEngine
from refunds.engine import RefundEngine
from wallets.engine import WalletEngine
from payouts.engine import PayoutEngine
from fraud.engine import FraudDetectionEngine
from health.monitor import HealthMonitor
from metrics.engine import MetricsEngine
from audit.engine import AuditEngine

app = FastAPI(
    title="MAHA Sales Engine - Commerce Platform API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

BASE_DIR = Path(__file__).parent.parent.parent.parent
CONFIG = ConfigManager(BASE_DIR / "config/engine.yaml")
DB = DatabaseManager(Path(CONFIG.get("database.path")))

commerce = CommerceCore(BASE_DIR)


# ============ MODELS ============

class CustomerCreate(BaseModel):
    email: str
    name: str
    language: str = "en"
    currency: str = "USD"


class OrderCreate(BaseModel):
    customer_id: str
    items: List[Dict[str, Any]]
    total_amount: float
    currency: str = "USD"


class PaymentRequestModel(BaseModel):
    order_id: str
    amount: float
    currency: str
    payment_method: str
    provider: str


class RefundRequest(BaseModel):
    order_id: str
    amount: float
    reason: str


class CouponValidate(BaseModel):
    code: str
    order_id: str


# ============ HEALTH ============

@app.get("/health")
async def health():
    return commerce.health_monitor.get_overall_health()


# ============ CUSTOMERS ============

@app.post("/api/v1/customers")
async def create_customer(customer: CustomerCreate):
    customer_id = commerce.customer_engine.create_customer(
        customer.email, customer.name, customer.language, customer.currency
    )
    if not customer_id:
        raise HTTPException(status_code=400, detail="Failed to create customer")
    return {"customer_id": customer_id, "status": "created"}


@app.get("/api/v1/customers/{customer_id}")
async def get_customer(customer_id: str):
    customer = commerce.customer_engine.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


# ============ ORDERS ============

@app.post("/api/v1/orders")
async def create_order(order: OrderCreate):
    order_id = commerce.order_engine.create_order(
        order.customer_id, order.items, order.total_amount, order.currency
    )
    if not order_id:
        raise HTTPException(status_code=400, detail="Failed to create order")
    return {"order_id": order_id, "status": "created"}


@app.get("/api/v1/orders/{order_id}")
async def get_order(order_id: str):
    order = commerce.order_engine.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.patch("/api/v1/orders/{order_id}/status")
async def update_order_status(order_id: str, status: str):
    success = commerce.order_engine.update_status(order_id, status)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update status")
    return {"order_id": order_id, "status": status}


# ============ CART ============

@app.post("/api/v1/cart")
async def create_cart(customer_id: str):
    cart_id = commerce.cart_engine.create_cart(customer_id)
    return {"cart_id": cart_id}


@app.post("/api/v1/cart/{cart_id}/items")
async def add_cart_item(cart_id: str, product_id: str, quantity: int = 1):
    commerce.cart_engine.add_item(cart_id, product_id, quantity)
    return {"cart_id": cart_id, "status": "updated"}


# ============ CHECKOUT ============

@app.post("/api/v1/checkout")
async def checkout(cart_id: str, payment_method: str):
    result = commerce.checkout_engine.checkout(cart_id, payment_method)
    return result


# ============ PAYMENTS ============

@app.post("/api/v1/payments/authorize")
async def authorize_payment(request: PaymentRequestModel):
    payment_request = PaymentRequest(
        amount=request.amount,
        currency=request.currency,
        method=request.payment_method,
        customer_id="",
        order_id=request.order_id
    )
    provider = commerce.payment_registry.get_provider(request.provider)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    import asyncio
    response = asyncio.run(provider.authorize(payment_request))
    return response.__dict__


@app.post("/api/v1/payments/verify/{transaction_id}")
async def verify_payment(transaction_id: str, provider: str):
    provider_instance = commerce.payment_registry.get_provider(provider)
    if not provider_instance:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    import asyncio
    response = asyncio.run(provider_instance.verify(transaction_id))
    return response.__dict__


# ============ LICENSES ============

@app.post("/api/v1/licenses")
async def issue_license(customer_id: str, product_id: str, order_id: str, license_type: str = "commercial"):
    license_id = commerce.license_engine.issue_license(customer_id, product_id, order_id, license_type)
    if not license_id:
        raise HTTPException(status_code=400, detail="Failed to issue license")
    return {"license_id": license_id, "status": "issued"}


@app.post("/api/v1/licenses/{license_id}/activate")
async def activate_license(license_id: str, activation_data: Dict[str, Any]):
    success = commerce.license_engine.activate_license(license_id, activation_data)
    return {"success": success}


@app.get("/api/v1/licenses/validate/{license_key}")
async def validate_license(license_key: str):
    license_data = commerce.license_engine.validate_license(license_key)
    if not license_data:
        raise HTTPException(status_code=404, detail="Invalid license")
    return license_data


# ============ SUBSCRIPTIONS ============

@app.post("/api/v1/subscriptions")
async def create_subscription(customer_id: str, product_id: str, plan_id: str):
    subscription_id = commerce.subscription_engine.create_subscription(customer_id, product_id, plan_id)
    return {"subscription_id": subscription_id}


@app.post("/api/v1/subscriptions/{subscription_id}/cancel")
async def cancel_subscription(subscription_id: str):
    success = commerce.subscription_engine.cancel_subscription(subscription_id)
    return {"success": success}


# ============ DELIVERIES ============

@app.post("/api/v1/deliveries")
async def create_delivery(order_id: str, product_id: str, file_path: str):
    delivery_id = commerce.delivery_engine.create_delivery(order_id, product_id, file_path)
    if not delivery_id:
        raise HTTPException(status_code=400, detail="Failed to create delivery")
    return {"delivery_id": delivery_id}


@app.get("/api/v1/deliveries/{delivery_id}/download")
async def get_download_url(delivery_id: str):
    url = commerce.delivery_engine.get_download_url(delivery_id)
    if not url:
        raise HTTPException(status_code=404, detail="Download not available")
    return {"download_url": url}


# ============ INVOICES ============

@app.post("/api/v1/invoices/generate/{order_id}")
async def generate_invoice(order_id: str):
    invoice_id = commerce.invoice_engine.generate_invoice(order_id)
    if not invoice_id:
        raise HTTPException(status_code=400, detail="Failed to generate invoice")
    return {"invoice_id": invoice_id}


# ============ REFUNDS ============

@app.post("/api/v1/refunds")
async def create_refund(request: RefundRequest):
    refund_id = commerce.refund_engine.create_refund(request.order_id, request.amount, request.reason)
    if not refund_id:
        raise HTTPException(status_code=400, detail="Failed to create refund")
    return {"refund_id": refund_id}


# ============ COUPONS ============

@app.post("/api/v1/coupons/validate")
async def validate_coupon(request: CouponValidate):
    coupon = commerce.coupon_engine.validate_coupon(request.code, request.order_id)
    if not coupon:
        raise HTTPException(status_code=404, detail="Invalid coupon")
    return coupon


# ============ PROMOTIONS ============

@app.get("/api/v1/promotions/active")
async def get_active_promotions():
    promotions = commerce.promotion_engine.get_active_promotions()
    return {"promotions": promotions}


# ============ METRICS ============

@app.get("/api/v1/metrics")
async def get_metrics():
    return commerce.metrics_engine.get_metrics()


# ============ AUDIT ============

@app.get("/api/v1/audit")
async def query_audit(resource_type: str = None, resource_id: str = None, limit: int = 100):
    logs = commerce.audit_engine.query(resource_type, resource_id, limit=limit)
    return {"logs": logs, "count": len(logs)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
