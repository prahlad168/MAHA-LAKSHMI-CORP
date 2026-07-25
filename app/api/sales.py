#!/usr/bin/env python3
"""
MAHA LAKSHMI AIOS - Sales & Revenue API
Digital product sales, orders, payments, and reporting.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/sales", tags=["sales"])

BASE_DIR = Path(__file__).parent.parent.parent
PRODUCTS_FILE = BASE_DIR / "sales-system" / "products.json"
ORDERS_FILE = BASE_DIR / "sales-system" / "orders.json"
CUSTOMERS_FILE = BASE_DIR / "sales-system" / "customers.json"


# ============================================================================
# DATA MODELS
# ============================================================================

class Product(BaseModel):
    id: str
    name: str
    category: str
    price_idr: float
    price_usd: float
    currency: str
    popular: bool
    features: List[str]
    active: bool


class OrderItem(BaseModel):
    product_id: str
    quantity: int = 1


class CustomerInfo(BaseModel):
    name: str
    email: str
    whatsapp: Optional[str] = None
    country: str = "Indonesia"


class CreateOrderRequest(BaseModel):
    customer: CustomerInfo
    items: List[OrderItem]
    payment_method: str = Field(..., description="bca, ewallet, usdt")
    currency: str = "IDR"


class VerifyPaymentRequest(BaseModel):
    order_id: str
    txid: Optional[str] = None
    sender_name: Optional[str] = None
    sender_bank: Optional[str] = None
    note: Optional[str] = None


class OrderResponse(BaseModel):
    order_id: str
    status: str
    total: float
    currency: str
    payment_method: str
    payment_details: Dict[str, Any]
    items: List[Dict[str, Any]]
    customer: Dict[str, Any]
    created_at: str


# ============================================================================
# HELPERS
# ============================================================================

def _load_json(path: Path) -> Dict:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(path: Path, data: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _now() -> str:
    return datetime.now().isoformat()


def _generate_order_id() -> str:
    return f"ORD-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


# ============================================================================
# PRODUCTS
# ============================================================================

@router.get("/products", response_model=List[Product])
async def list_products():
    data = _load_json(PRODUCTS_FILE)
    return [p for p in data.get("products", []) if p.get("active")]


@router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    data = _load_json(PRODUCTS_FILE)
    for p in data.get("products", []):
        if p.get("id") == product_id and p.get("active"):
            return p
    raise HTTPException(status_code=404, detail="Product not found")


# ============================================================================
# ORDERS
# ============================================================================

@router.post("/orders", response_model=OrderResponse)
async def create_order(request: CreateOrderRequest):
    products_data = _load_json(PRODUCTS_FILE)
    orders_data = _load_json(ORDERS_FILE)
    customers_data = _load_json(CUSTOMERS_FILE)

    products_by_id = {p["id"]: p for p in products_data.get("products", [])}

    order_items = []
    total = 0.0
    for item in request.items:
        product = products_by_id.get(item.product_id)
        if not product or not product.get("active"):
            raise HTTPException(status_code=400, detail=f"Invalid product: {item.product_id}")
        line_total = product.get("price_idr" if request.currency == "IDR" else "price_usd", 0) * item.quantity
        total += line_total
        order_items.append({
            "product_id": product["id"],
            "name": product["name"],
            "price": line_total,
            "currency": request.currency,
            "quantity": item.quantity,
        })

    payment_methods = products_data.get("payment_methods", {})
    method_info = payment_methods.get(request.payment_method, {})
    if not method_info:
        raise HTTPException(status_code=400, detail="Invalid payment method")

    order_id = _generate_order_id()
    order = {
        "order_id": order_id,
        "status": "pending",
        "total": total,
        "currency": request.currency,
        "payment_method": request.payment_method,
        "payment_details": {
            "method": request.payment_method,
            "label": method_info.get("label", request.payment_method),
            "info": method_info,
            "note": f"Transfer sesuai nominal {request.currency} {total:,.0f} dan kirim bukti ke WhatsApp.",
        },
        "items": order_items,
        "customer": request.customer.model_dump(mode="json"),
        "created_at": _now(),
        "updated_at": _now(),
        "verified_at": None,
        "txid": None,
    }

    orders_data.setdefault("orders", []).append(order)
    orders_data["next_id"] = orders_data.get("next_id", 0) + 1
    _save_json(ORDERS_FILE, orders_data)

    customer = request.customer.model_dump(mode="json")
    customer.setdefault("orders", []).append(order_id)
    customer["updated_at"] = _now()
    customers_data.setdefault("customers", []).append(customer)
    _save_json(CUSTOMERS_FILE, customers_data)

    return OrderResponse(
        order_id=order_id,
        status=order["status"],
        total=order["total"],
        currency=order["currency"],
        payment_method=order["payment_method"],
        payment_details=order["payment_details"],
        items=order["items"],
        customer=order["customer"],
        created_at=order["created_at"],
    )


@router.get("/orders", response_model=List[Dict[str, Any]])
async def list_orders(status: Optional[str] = None):
    data = _load_json(ORDERS_FILE)
    orders = data.get("orders", [])
    if status:
        orders = [o for o in orders if o.get("status") == status]
    return orders


@router.get("/orders/{order_id}", response_model=Dict[str, Any])
async def get_order(order_id: str):
    data = _load_json(ORDERS_FILE)
    for order in data.get("orders", []):
        if order.get("order_id") == order_id:
            return order
    raise HTTPException(status_code=404, detail="Order not found")


@router.post("/orders/{order_id}/verify", response_model=Dict[str, Any])
async def verify_payment(order_id: str, request: VerifyPaymentRequest):
    data = _load_json(ORDERS_FILE)
    for order in data.get("orders", []):
        if order.get("order_id") == order_id:
            order["status"] = "paid"
            order["verified_at"] = _now()
            order["txid"] = request.txid
            order["sender_name"] = request.sender_name
            order["sender_bank"] = request.sender_bank
            order["note"] = request.note
            order["updated_at"] = _now()
            _save_json(ORDERS_FILE, data)
            return {"success": True, "order_id": order_id, "status": "paid", "message": "Payment verified"}
    raise HTTPException(status_code=404, detail="Order not found")


# ============================================================================
# REPORTS
# ============================================================================

@router.get("/reports/daily")
async def daily_report(date: Optional[str] = None):
    data = _load_json(ORDERS_FILE)
    orders = data.get("orders", [])
    if date:
        orders = [o for o in orders if o.get("created_at", "").startswith(date)]
    else:
        today = datetime.now().date().isoformat()
        orders = [o for o in orders if o.get("created_at", "").startswith(today)]

    total = sum(o.get("total", 0) for o in orders if o.get("status") == "paid")
    pending = sum(o.get("total", 0) for o in orders if o.get("status") == "pending")
    by_method: Dict[str, float] = {}
    for o in orders:
        if o.get("status") == "paid":
            by_method[o.get("payment_method", "unknown")] = by_method.get(o.get("payment_method", "unknown"), 0) + o.get("total", 0)

    return {
        "date": date or datetime.now().date().isoformat(),
        "total_orders": len(orders),
        "paid_orders": len([o for o in orders if o.get("status") == "paid"]),
        "pending_orders": len([o for o in orders if o.get("status") == "pending"]),
        "total_revenue": total,
        "pending_revenue": pending,
        "by_payment_method": by_method,
        "ceo_share_usdt": {
            "share_percent": 100,
            "amount_idr": total,
            "wallet": "TNFs1SP2C8HxGSZkSH3hJamf8ukgtnW7U6",
            "network": "TRC20",
        },
    }


@router.get("/reports/transactions")
async def transaction_history(limit: int = 100, status: Optional[str] = None):
    data = _load_json(ORDERS_FILE)
    orders = data.get("orders", [])
    if status:
        orders = [o for o in orders if o.get("status") == status]
    orders = sorted(orders, key=lambda x: x.get("created_at", ""), reverse=True)[:limit]
    return {"count": len(orders), "transactions": orders}


@router.get("/reports/summary")
async def revenue_summary():
    data = _load_json(ORDERS_FILE)
    orders = data.get("orders", [])
    paid = [o for o in orders if o.get("status") == "paid"]
    pending = [o for o in orders if o.get("status") == "pending"]

    total_paid = sum(o.get("total", 0) for o in paid)
    total_pending = sum(o.get("total", 0) for o in pending)

    by_product: Dict[str, Dict[str, Any]] = {}
    for o in paid:
        for item in o.get("items", []):
            pid = item.get("product_id")
            if pid not in by_product:
                by_product[pid] = {"count": 0, "revenue": 0, "name": item.get("name", pid)}
            by_product[pid]["count"] += item.get("quantity", 1)
            by_product[pid]["revenue"] += item.get("price", 0)

    return {
        "total_transactions": len(orders),
        "paid_transactions": len(paid),
        "pending_transactions": len(pending),
        "total_revenue_idr": total_paid,
        "pending_revenue_idr": total_pending,
        "ceo_share": {
            "percent": 100,
            "amount_idr": total_paid,
            "wallet": "TNFs1SP2C8HxGSZkSH3hJamf8ukgtnW7U6",
            "network": "TRC20",
        },
        "by_product": by_product,
    }


@router.get("/customers")
async def list_customers():
    data = _load_json(CUSTOMERS_FILE)
    customers = data.get("customers", [])
    return {"count": len(customers), "customers": customers}
