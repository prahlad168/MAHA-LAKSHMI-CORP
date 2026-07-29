#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Customer Engine
Customer and organization management.
"""

import os
import sys
import json
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.commerce.customers")


@dataclass
class Customer:
    customer_id: str
    email: str
    name: str
    language: str
    currency: str
    billing_profile: Dict[str, Any]
    purchase_history: List[str]
    subscription_history: List[str]
    license_history: List[str]
    download_history: List[str]
    created_at: str
    updated_at: str


class CustomerEngine:
    """Manage customers"""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def create_customer(self, email: str, name: str, language: str = "en", 
                        currency: str = "USD") -> Optional[str]:
        try:
            customer_id = f"cust-{uuid.uuid4().hex[:12]}"
            now = datetime.now().isoformat()
            
            customer = Customer(
                customer_id=customer_id,
                email=email,
                name=name,
                language=language,
                currency=currency,
                billing_profile={},
                purchase_history=[],
                subscription_history=[],
                license_history=[],
                download_history=[],
                created_at=now,
                updated_at=now
            )
            
            self._save_customer(customer)
            logger.info(f"Customer created: {customer_id}")
            return customer_id
        except Exception as e:
            logger.error(f"Failed to create customer: {e}")
            return None
    
    def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Failed to get customer: {e}")
            return None
    
    def _save_customer(self, customer: Customer):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO customers 
                (customer_id, email, name, language, currency, billing_profile,
                 purchase_history, subscription_history, license_history, download_history,
                 created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                customer.customer_id, customer.email, customer.name,
                customer.language, customer.currency, json.dumps(customer.billing_profile),
                json.dumps(customer.purchase_history), json.dumps(customer.subscription_history),
                json.dumps(customer.license_history), json.dumps(customer.download_history),
                customer.created_at, customer.updated_at
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to save customer: {e}")


def main():
    print("Customer Engine initialized")


if __name__ == "__main__":
    main()
