#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Order Engine
Order management with state machine.
"""

import os
import sys
import json
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from orders.state_machine import OrderStateMachine, OrderStatusManager

logger = logging.getLogger("maha-sales-engine.commerce.orders")


class OrderEngine:
    """Manage orders"""
    
    def __init__(self, db_manager, event_bus):
        self.db = db_manager
        self.event_bus = event_bus
        self.state_manager = OrderStatusManager()
    
    def create_order(self, customer_id: str, items: List[Dict[str, Any]], 
                     total_amount: float, currency: str = "USD") -> Optional[str]:
        try:
            order_id = f"order-{uuid.uuid4().hex[:12]}"
            now = datetime.now().isoformat()
            
            order = {
                "order_id": order_id,
                "customer_id": customer_id,
                "items": json.dumps(items),
                "total_amount": total_amount,
                "currency": currency,
                "status": OrderStatus.DRAFT.value,
                "created_at": now,
                "updated_at": now
            }
            
            self._save_order(order)
            logger.info(f"Order created: {order_id}")
            return order_id
        except Exception as e:
            logger.error(f"Failed to create order: {e}")
            return None
    
    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Failed to get order: {e}")
            return None
    
    def update_status(self, order_id: str, new_status: str) -> bool:
        try:
            order = self.get_order(order_id)
            if not order:
                return False
            
            result = self.state_manager.transition(order, new_status)
            if not result["success"]:
                logger.warning(f"Invalid transition: {result['error']}")
                return False
            
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE orders SET status = ?, updated_at = ? WHERE order_id = ?",
                         (new_status, datetime.now().isoformat(), order_id))
            conn.commit()
            
            logger.info(f"Order status updated: {order_id} -> {new_status}")
            return True
        except Exception as e:
            logger.error(f"Failed to update order status: {e}")
            return False
    
    def _save_order(self, order: Dict[str, Any]):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO orders 
                (order_id, customer_id, items, total_amount, currency, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                order["order_id"], order["customer_id"], order["items"],
                order["total_amount"], order["currency"], order["status"],
                order["created_at"], order["updated_at"]
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to save order: {e}")


def main():
    print("Order Engine initialized")


if __name__ == "__main__":
    main()
