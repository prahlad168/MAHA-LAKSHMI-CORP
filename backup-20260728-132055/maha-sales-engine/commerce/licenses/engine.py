#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - License Engine
License generation, activation, and management.
"""

import os
import sys
import json
import uuid
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.commerce.licenses")


class LicenseType(Enum):
    PERSONAL = "personal"
    COMMERCIAL = "commercial"
    EXTENDED = "extended"
    ENTERPRISE = "enterprise"
    SUBSCRIPTION = "subscription"
    LIFETIME = "lifetime"
    TRIAL = "trial"
    CUSTOM = "custom"


class LicenseStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"


@dataclass
class License:
    license_id: str
    customer_id: str
    product_id: str
    order_id: str
    license_type: str
    status: str
    key: str
    activated_at: Optional[str]
    expires_at: Optional[str]
    activations: int
    max_activations: int
    metadata: Dict[str, Any]
    created_at: str


class LicenseEngine:
    """Manage licenses"""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def issue_license(self, customer_id: str, product_id: str, order_id: str,
                      license_type: str, metadata: Dict[str, Any] = None) -> Optional[str]:
        try:
            license_id = f"lic-{uuid.uuid4().hex[:12]}"
            key = self._generate_license_key(license_id, product_id)
            now = datetime.now().isoformat()
            
            license_data = {
                "license_id": license_id,
                "customer_id": customer_id,
                "product_id": product_id,
                "order_id": order_id,
                "license_type": license_type,
                "status": LicenseStatus.ACTIVE.value,
                "key": key,
                "activated_at": None,
                "expires_at": None,
                "activations": 0,
                "max_activations": metadata.get("max_activations", 1) if metadata else 1,
                "metadata": json.dumps(metadata or {}),
                "created_at": now
            }
            
            self._save_license(license_data)
            logger.info(f"License issued: {license_id}")
            return license_id
        except Exception as e:
            logger.error(f"Failed to issue license: {e}")
            return None
    
    def activate_license(self, license_id: str, activation_data: Dict[str, Any]) -> bool:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM licenses WHERE license_id = ?", (license_id,))
            row = cursor.fetchone()
            
            if not row:
                return False
            
            license_data = dict(row)
            if license_data["activations"] >= license_data["max_activations"]:
                return False
            
            now = datetime.now().isoformat()
            cursor.execute("""
                UPDATE licenses 
                SET activated_at = ?, activations = activations + 1, updated_at = ?
                WHERE license_id = ?
            """, (now, now, license_id))
            conn.commit()
            
            logger.info(f"License activated: {license_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to activate license: {e}")
            return False
    
    def validate_license(self, license_key: str) -> Optional[Dict[str, Any]]:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM licenses WHERE key = ?", (license_key,))
            row = cursor.fetchone()
            
            if row:
                license_data = dict(row)
                if license_data["status"] == LicenseStatus.ACTIVE.value:
                    return license_data
            return None
        except Exception as e:
            logger.error(f"License validation failed: {e}")
            return None
    
    def _generate_license_key(self, license_id: str, product_id: str) -> str:
        raw = f"{license_id}:{product_id}:{datetime.now().isoformat()}"
        return hashlib.sha256(raw.encode()).hexdigest()[:32].upper()
    
    def _save_license(self, license_data: Dict[str, Any]):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO licenses 
                (license_id, customer_id, product_id, order_id, license_type, status,
                 key, activated_at, expires_at, activations, max_activations, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                license_data["license_id"], license_data["customer_id"],
                license_data["product_id"], license_data["order_id"],
                license_data["license_type"], license_data["status"],
                license_data["key"], license_data["activated_at"],
                license_data["expires_at"], license_data["activations"],
                license_data["max_activations"], license_data["metadata"],
                license_data["created_at"]
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to save license: {e}")


def main():
    print("License Engine initialized")


if __name__ == "__main__":
    main()
