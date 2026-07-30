#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Audit Engine
Immutable audit trail for compliance.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.sales-automation.audit")


class AuditEngine:
    """Immutable audit trail"""
    
    def __init__(self, db_manager, event_bus):
        self.db = db_manager
        self.event_bus = event_bus
    
    def log(self, action: str, actor: str, resource_type: str, resource_id: str,
            before: Optional[Dict] = None, after: Optional[Dict] = None,
            ip_address: str = "", result: str = "success",
            metadata: Dict[str, Any] = None):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_log 
                (id, action, actor, resource_type, resource_id, before_data, after_data,
                 ip_address, result, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"audit-{uuid.uuid4().hex[:12]}",
                action,
                actor,
                resource_type,
                resource_id,
                json.dumps(before) if before else None,
                json.dumps(after) if after else None,
                ip_address,
                result,
                json.dumps(metadata or {}),
                datetime.now().isoformat()
            ))
            conn.commit()
            
            logger.debug(f"Audit log: {action} on {resource_type}:{resource_id}")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def query(self, resource_type: str = None, resource_id: str = None,
              action: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM audit_log WHERE 1=1"
            params = []
            
            if resource_type:
                query += " AND resource_type = ?"
                params.append(resource_type)
            if resource_id:
                query += " AND resource_id = ?"
                params.append(resource_id)
            if action:
                query += " AND action = ?"
                params.append(action)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to query audit log: {e}")
            return []


def main():
    print("Audit Engine initialized")


if __name__ == "__main__":
    main()
