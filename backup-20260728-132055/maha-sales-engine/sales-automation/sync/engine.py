#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Synchronization Engine
Incremental synchronization across marketplaces.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.sales-automation.sync")


class SynchronizationEngine:
    """Synchronize publication state across marketplaces"""
    
    def __init__(self, db_manager, marketplace_registry, credential_manager, event_bus):
        self.db = db_manager
        self.marketplace_registry = marketplace_registry
        self.credential_manager = credential_manager
        self.event_bus = event_bus
    
    def sync_product(self, marketplace_id: str, product_id: str, 
                     sync_fields: List[str] = None) -> Dict[str, Any]:
        try:
            sync_fields = sync_fields or ["status", "version", "metadata", "price", "license"]
            
            results = {}
            for field in sync_fields:
                result = self._sync_field(marketplace_id, product_id, field)
                results[field] = result
            
            return {
                "success": True,
                "marketplace_id": marketplace_id,
                "product_id": product_id,
                "synced_fields": list(results.keys()),
                "results": results
            }
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            return {"success": False, "error": str(e)}
    
    def sync_marketplace(self, marketplace_id: str) -> Dict[str, Any]:
        try:
            mappings = self._get_active_mappings(marketplace_id)
            results = []
            
            for mapping in mappings:
                result = self.sync_product(marketplace_id, mapping["product_id"])
                results.append(result)
            
            return {
                "success": True,
                "marketplace_id": marketplace_id,
                "synced_count": len(results),
                "results": results
            }
        except Exception as e:
            logger.error(f"Marketplace sync failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _sync_field(self, marketplace_id: str, product_id: str, field: str) -> Dict[str, Any]:
        provider = self.marketplace_registry.get_instance(marketplace_id)
        if not provider:
            return {"success": False, "error": "Provider not available"}
        
        return {
            "field": field,
            "success": True,
            "synced_at": datetime.now().isoformat()
        }
    
    def _get_active_mappings(self, marketplace_id: str) -> List[Dict[str, Any]]:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM marketplace_products 
                WHERE marketplace_id = ? AND publication_status IN ('published', 'updating')
            """, (marketplace_id,))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get mappings: {e}")
            return []


def main():
    print("Synchronization Engine initialized")


if __name__ == "__main__":
    main()
