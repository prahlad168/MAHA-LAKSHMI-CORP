#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Webhook Gateway
Webhook receiving, validation, routing, and replay protection.
"""

import os
import sys
import json
import hashlib
import hmac
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.sales-automation.webhooks")


class WebhookGateway:
    """Webhook receiving, validation, and routing"""
    
    def __init__(self, db_manager, event_bus):
        self.db = db_manager
        self.event_bus = event_bus
        self._routes: Dict[str, Dict[str, Any]] = {}
        self._processed_ids: set = set()
    
    def register_route(self, marketplace_id: str, event_types: List[str],
                       secret: str = "", handler=None):
        route_id = f"route-{marketplace_id}"
        self._routes[route_id] = {
            "marketplace_id": marketplace_id,
            "event_types": event_types,
            "secret": secret,
            "handler": handler,
            "active": True
        }
        logger.info(f"Webhook route registered: {route_id}")
    
    async def process_webhook(self, marketplace_id: str, payload: Dict[str, Any],
                              signature: str = "", headers: Dict[str, str] = None) -> Dict[str, Any]:
        try:
            route_id = f"route-{marketplace_id}"
            route = self._routes.get(route_id)
            
            if not route or not route.get("active"):
                return {"success": False, "error": "Route not found or inactive"}
            
            # Validate signature
            if route.get("secret"):
                if not self._validate_signature(payload, signature, route["secret"]):
                    return {"success": False, "error": "Invalid signature"}
            
            # Replay protection
            event_id = payload.get("id") or payload.get("event_id")
            if event_id in self._processed_ids:
                return {"success": False, "error": "Duplicate event"}
            
            if event_id:
                self._processed_ids.add(event_id)
            
            # Route event
            event_type = payload.get("event_type", "unknown")
            if event_type not in route.get("event_types", []):
                return {"success": False, "error": f"Unsupported event type: {event_type}"}
            
            # Log webhook
            self._log_webhook(marketplace_id, payload, "processed")
            
            # Call handler
            handler = route.get("handler")
            if handler:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(payload)
                    else:
                        handler(payload)
                except Exception as e:
                    logger.error(f"Webhook handler failed: {e}")
                    return {"success": False, "error": str(e)}
            
            return {"success": True, "processed": True}
        except Exception as e:
            logger.error(f"Webhook processing failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _validate_signature(self, payload: Dict[str, Any], signature: str, secret: str) -> bool:
        if not signature:
            return False
        expected = hmac.new(
            secret.encode(),
            json.dumps(payload).encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
    
    def _log_webhook(self, marketplace_id: str, payload: Dict[str, Any], status: str):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO webhook_logs (id, marketplace_id, payload, status, received_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                f"wh-{uuid.uuid4().hex[:12]}",
                marketplace_id,
                json.dumps(payload),
                status,
                datetime.now().isoformat()
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to log webhook: {e}")


def main():
    print("Webhook Gateway initialized")


if __name__ == "__main__":
    main()
