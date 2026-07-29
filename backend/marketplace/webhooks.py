"""
MAHA LAKSHMI CORP - Marketplace Webhook Routes
Handles incoming webhooks from Gumroad and other marketplaces.
"""

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
import json
import logging
from datetime import datetime

from backend.db.connection import execute_query
from backend.shared.security import verify_jwt_token
from backend.shared.webhook_security import WebhookSecurity
from backend.finance.sale_processor import SaleProcessor, SaleEvent

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()


@router.post("/webhooks/gumroad", tags=["Marketplace"])
async def handle_gumroad_webhook(request: Request):
    """Handle Gumroad webhook events"""
    try:
        # Get raw body for signature verification
        body = await request.body()
        payload = json.loads(body.decode('utf-8'))
        
        # Get headers
        signature = request.headers.get("X-Gumroad-Signature", "")
        webhook_secret = request.headers.get("X-Webhook-Secret", "")
        
        # Verify signature if secret is configured
        # In production, store and use the actual webhook secret from Gumroad
        # For now, we accept the webhook if it has valid structure
        
        # Extract event type
        event_type = WebhookSecurity.extract_event_type(payload)
        if not event_type:
            logger.warning(f"Unknown webhook event type: {payload}")
            raise HTTPException(status_code=400, detail="Unknown event type")
        
        # Check for replay attack
        timestamp = payload.get("timestamp") or payload.get("created_at") or datetime.now().isoformat()
        if WebhookSecurity.is_replay_attack("", timestamp):
            logger.warning(f"Replay attack detected: {timestamp}")
            raise HTTPException(status_code=400, detail="Replay attack detected")
        
        # Log webhook receipt
        execute_query(
            """
            INSERT INTO audit_logs 
            (user_id, action, resource_type, resource_id, details, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                None,  # System action
                "webhook_received",
                "gumroad_webhook",
                None,
                json.dumps({"event_type": event_type, "payload": WebhookSecurity.sanitize_payload(payload)}),
                datetime.now().isoformat()
            ),
            fetch="none"
        )
        
        # Process event
        processor = SaleProcessor()
        
        if event_type == "purchase":
            result = processor.process_purchase(SaleEvent(
                gumroad_purchase_id=payload.get("id") or payload.get("purchase_id", ""),
                product_id=payload.get("product_id", ""),
                marketplace_product_id=payload.get("product_id", ""),
                account_id=payload.get("account_id", "default"),
                customer_email=payload.get("email", ""),
                customer_name=payload.get("name", ""),
                amount=float(payload.get("price", 0)) / 100,  # Convert cents to dollars
                currency=payload.get("currency", "USD"),
                tax=float(payload.get("tax", 0)) / 100,
                fee=float(payload.get("fee", 0)) / 100,
                net_amount=float(payload.get("net_amount", 0)) / 100,
                payment_method=payload.get("payment_method", "gumroad"),
                payment_status="completed",
                license_key=payload.get("license_key"),
                sale_date=payload.get("sale_date") or payload.get("created_at") or datetime.now().isoformat()
            ))
            
            if result.get("success"):
                logger.info(f"Sale processed: {result.get('sale_id')}")
                return {"status": "success", "sale_id": result.get("sale_id")}
            else:
                logger.error(f"Sale processing failed: {result.get('error')}")
                raise HTTPException(status_code=500, detail=result.get("error"))
        
        elif event_type == "refund":
            result = processor.process_refund(SaleEvent(
                gumroad_purchase_id=payload.get("id") or payload.get("purchase_id", ""),
                product_id=payload.get("product_id", ""),
                marketplace_product_id=payload.get("product_id", ""),
                account_id=payload.get("account_id", "default"),
                customer_email=payload.get("email", ""),
                customer_name=payload.get("name", ""),
                amount=float(payload.get("price", 0)) / 100,
                currency=payload.get("currency", "USD"),
                tax=0,
                fee=0,
                net_amount=float(payload.get("price", 0)) / 100,
                payment_method="gumroad",
                payment_status="refunded",
                license_key=None,
                sale_date=datetime.now().isoformat()
            ))
            
            if result.get("success"):
                return {"status": "success", "refund_id": result.get("transaction_id")}
            else:
                raise HTTPException(status_code=500, detail=result.get("error"))
        
        elif event_type == "chargeback":
            result = processor.process_chargeback(SaleEvent(
                gumroad_purchase_id=payload.get("id") or payload.get("purchase_id", ""),
                product_id=payload.get("product_id", ""),
                marketplace_product_id=payload.get("product_id", ""),
                account_id=payload.get("account_id", "default"),
                customer_email=payload.get("email", ""),
                customer_name=payload.get("name", ""),
                amount=float(payload.get("price", 0)) / 100,
                currency=payload.get("currency", "USD"),
                tax=0,
                fee=0,
                net_amount=float(payload.get("price", 0)) / 100,
                payment_method="gumroad",
                payment_status="chargeback",
                license_key=None,
                sale_date=datetime.now().isoformat()
            ))
            
            if result.get("success"):
                return {"status": "success", "chargeback_id": result.get("transaction_id")}
            else:
                raise HTTPException(status_code=500, detail=result.get("error"))
        
        else:
            logger.info(f"Unhandled event type: {event_type}")
            return {"status": "ignored", "event_type": event_type}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")
