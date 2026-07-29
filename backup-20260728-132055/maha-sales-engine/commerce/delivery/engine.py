#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Digital Delivery Engine
Secure digital product delivery and download management.
"""

import os
import sys
import json
import uuid
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.commerce.delivery")


class DigitalDeliveryEngine:
    """Manage digital product delivery"""
    
    def __init__(self, db_manager, output_dir: Path):
        self.db = db_manager
        self.output_dir = output_dir
        self.download_base_url = "/downloads"
    
    def create_delivery(self, order_id: str, product_id: str, 
                        file_path: str, expires_in_hours: int = 24) -> Optional[str]:
        try:
            delivery_id = f"del-{uuid.uuid4().hex[:12]}"
            token = self._generate_download_token(delivery_id, product_id)
            expires_at = (datetime.now() + timedelta(hours=expires_in_hours)).isoformat()
            
            delivery = {
                "delivery_id": delivery_id,
                "order_id": order_id,
                "product_id": product_id,
                "file_path": file_path,
                "download_token": token,
                "download_url": f"{self.download_base_url}/{token}",
                "expires_at": expires_at,
                "download_count": 0,
                "max_downloads": 5,
                "created_at": datetime.now().isoformat()
            }
            
            self._save_delivery(delivery)
            logger.info(f"Delivery created: {delivery_id}")
            return delivery_id
        except Exception as e:
            logger.error(f"Failed to create delivery: {e}")
            return None
    
    def get_download_url(self, delivery_id: str) -> Optional[str]:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM deliveries WHERE delivery_id = ?", (delivery_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            delivery = dict(row)
            if datetime.fromisoformat(delivery["expires_at"]) < datetime.now():
                return None
            
            return delivery["download_url"]
        except Exception as e:
            logger.error(f"Failed to get download URL: {e}")
            return None
    
    def record_download(self, delivery_id: str, ip_address: str, user_agent: str) -> bool:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE deliveries 
                SET download_count = download_count + 1, last_downloaded_at = ?
                WHERE delivery_id = ?
            """, (datetime.now().isoformat(), delivery_id))
            conn.commit()
            
            cursor.execute("""
                INSERT INTO download_logs (download_id, delivery_id, ip_address, user_agent, downloaded_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                f"dl-{uuid.uuid4().hex[:12]}",
                delivery_id,
                ip_address,
                user_agent,
                datetime.now().isoformat()
            ))
            conn.commit()
            
            return True
        except Exception as e:
            logger.error(f"Failed to record download: {e}")
            return False
    
    def _generate_download_token(self, delivery_id: str, product_id: str) -> str:
        raw = f"{delivery_id}:{product_id}:{datetime.now().isoformat()}"
        return hashlib.sha256(raw.encode()).hexdigest()[:32]
    
    def _save_delivery(self, delivery: Dict[str, Any]):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO deliveries 
                (delivery_id, order_id, product_id, file_path, download_token,
                 download_url, expires_at, download_count, max_downloads, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                delivery["delivery_id"], delivery["order_id"], delivery["product_id"],
                delivery["file_path"], delivery["download_token"], delivery["download_url"],
                delivery["expires_at"], delivery["download_count"], delivery["max_downloads"],
                delivery["created_at"]
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to save delivery: {e}")


def main():
    print("Digital Delivery Engine initialized")


if __name__ == "__main__":
    main()
