#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Approval Engine
Human-in-the-loop approval workflows.
"""

import os
import sys
import json
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.sales-automation.approval")


class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


@dataclass
class ApprovalRequest:
    request_id: str
    workflow_id: str
    execution_id: str
    marketplace_id: str
    product_id: str
    approval_type: str
    status: str
    requested_by: str
    approved_by: Optional[str]
    feedback: Optional[str]
    requested_at: str
    responded_at: Optional[str]
    expires_at: Optional[str]
    metadata: Dict[str, Any]


class ApprovalEngine:
    """Manage approval workflows"""
    
    def __init__(self, db_manager, event_bus, notification_engine):
        self.db = db_manager
        self.event_bus = event_bus
        self.notification_engine = notification_engine
    
    def request_approval(self, marketplace_id: str, product_id: str, 
                        approval_type: str, metadata: Dict[str, Any] = None) -> str:
        try:
            request_id = f"appr-{uuid.uuid4().hex[:12]}"
            now = datetime.now().isoformat()
            expires_at = (datetime.now().timestamp() + 7 * 24 * 3600)
            
            request = ApprovalRequest(
                request_id=request_id,
                workflow_id=metadata.get("workflow_id", ""),
                execution_id=metadata.get("execution_id", ""),
                marketplace_id=marketplace_id,
                product_id=product_id,
                approval_type=approval_type,
                status=ApprovalStatus.PENDING.value,
                requested_by="system",
                approved_by=None,
                feedback=None,
                requested_at=now,
                responded_at=None,
                expires_at=datetime.fromtimestamp(expires_at).isoformat(),
                metadata=metadata or {}
            )
            
            self._save_request(request)
            self.notification_engine.send_notification(
                channel="email",
                recipient="admin@maha.com",
                subject=f"Approval Required: {approval_type}",
                body=f"Approval required for marketplace {marketplace_id}, product {product_id}"
            )
            
            logger.info(f"Approval requested: {request_id}")
            return request_id
        except Exception as e:
            logger.error(f"Failed to request approval: {e}")
            return ""
    
    def approve(self, request_id: str, approved_by: str, feedback: str = "") -> bool:
        try:
            request = self._load_request(request_id)
            if not request:
                return False
            
            request.status = ApprovalStatus.APPROVED.value
            request.approved_by = approved_by
            request.feedback = feedback
            request.responded_at = datetime.now().isoformat()
            
            self._save_request(request)
            logger.info(f"Approval granted: {request_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to approve: {e}")
            return False
    
    def reject(self, request_id: str, rejected_by: str, feedback: str = "") -> bool:
        try:
            request = self._load_request(request_id)
            if not request:
                return False
            
            request.status = ApprovalStatus.REJECTED.value
            request.approved_by = rejected_by
            request.feedback = feedback
            request.responded_at = datetime.now().isoformat()
            
            self._save_request(request)
            logger.info(f"Approval rejected: {request_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to reject: {e}")
            return False
    
    def _save_request(self, request: ApprovalRequest):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO approval_requests 
                (request_id, workflow_id, execution_id, marketplace_id, product_id,
                 approval_type, status, requested_by, approved_by, feedback,
                 requested_at, responded_at, expires_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                request.request_id, request.workflow_id, request.execution_id,
                request.marketplace_id, request.product_id, request.approval_type,
                request.status, request.requested_by, request.approved_by, request.feedback,
                request.requested_at, request.responded_at, request.expires_at,
                json.dumps(request.metadata)
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to save approval request: {e}")
    
    def _load_request(self, request_id: str) -> Optional[ApprovalRequest]:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM approval_requests WHERE request_id = ?", (request_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return ApprovalRequest(
                request_id=row["request_id"],
                workflow_id=row["workflow_id"],
                execution_id=row["execution_id"],
                marketplace_id=row["marketplace_id"],
                product_id=row["product_id"],
                approval_type=row["approval_type"],
                status=row["status"],
                requested_by=row["requested_by"],
                approved_by=row.get("approved_by"),
                feedback=row.get("feedback"),
                requested_at=row["requested_at"],
                responded_at=row.get("responded_at"),
                expires_at=row.get("expires_at"),
                metadata=json.loads(row.get("metadata", "{}"))
            )
        except Exception as e:
            logger.error(f"Failed to load approval request: {e}")
            return None


def main():
    print("Approval Engine initialized")


if __name__ == "__main__":
    main()
