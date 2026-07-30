#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Publication Engine
Single and bulk publication operations.
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

logger = logging.getLogger("maha-sales-engine.sales-automation.publication")


class PublicationEngine:
    """Handle single and bulk publication operations"""
    
    def __init__(self, db_manager, marketplace_registry, credential_manager, 
                 event_bus, workflow_engine, approval_engine, rules_engine):
        self.db = db_manager
        self.marketplace_registry = marketplace_registry
        self.credential_manager = credential_manager
        self.event_bus = event_bus
        self.workflow_engine = workflow_engine
        self.approval_engine = approval_engine
        self.rules_engine = rules_engine
    
    def publish_single(self, marketplace_id: str, product_id: str, 
                       product_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Validate rules
            validation = self.rules_engine.validate_publication(marketplace_id, product_id, product_data)
            if not validation.get("valid", False):
                return {"success": False, "error": validation.get("error")}
            
            # Check approval if required
            if self.rules_engine.requires_approval(marketplace_id, product_id):
                approval_id = self.approval_engine.request_approval(
                    marketplace_id, product_id, "publication"
                )
                return {
                    "success": True,
                    "status": "awaiting_approval",
                    "approval_id": approval_id
                }
            
            # Execute publication via workflow
            workflow_id = self._get_workflow_for_marketplace(marketplace_id)
            execution_id = self.workflow_engine.start_workflow(workflow_id, {
                "marketplace_id": marketplace_id,
                "product_id": product_id,
                "product_data": product_data
            })
            
            return {
                "success": True,
                "execution_id": execution_id,
                "status": "queued"
            }
        except Exception as e:
            logger.error(f"Single publish failed: {e}")
            return {"success": False, "error": str(e)}
    
    def publish_bulk(self, marketplace_id: str, product_ids: List[str], 
                     product_data_map: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        try:
            results = []
            for product_id in product_ids:
                product_data = product_data_map.get(product_id, {})
                result = self.publish_single(marketplace_id, product_id, product_data)
                results.append({
                    "product_id": product_id,
                    "result": result
                })
            
            return {
                "success": True,
                "total": len(product_ids),
                "results": results
            }
        except Exception as e:
            logger.error(f"Bulk publish failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_workflow_for_marketplace(self, marketplace_id: str) -> str:
        return "default-publication-workflow"


def main():
    print("Publication Engine initialized")


if __name__ == "__main__":
    main()
