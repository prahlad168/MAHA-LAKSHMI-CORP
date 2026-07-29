#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Approval Workflow
Manages approval workflow for optimizations requiring human approval.
"""

import os
import sys
import json
import time
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.optimization.approval")


class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class ApprovalRequest:
    request_id: str
    optimization_id: str
    decision_id: str
    requester: str
    approver: Optional[str]
    status: ApprovalStatus
    reason: str
    context: Dict[str, Any]
    expires_at: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    decided_at: Optional[str] = None


class ApprovalWorkflow:
    """
    Approval workflow for optimizations requiring human approval.
    """
    
    def __init__(self, db_manager):
        self.db = db_manager
        self._requests: Dict[str, ApprovalRequest] = {}
        self.default_expiry_hours = 24
    
    def create_request(self, optimization_id: str, decision_id: str, requester: str, reason: str, context: Dict[str, Any]) -> ApprovalRequest:
        """Create approval request"""
        request_id = f"appr-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
        expires_at = (datetime.now() + timedelta(hours=self.default_expiry_hours)).isoformat()
        
        request = ApprovalRequest(
            request_id=request_id,
            optimization_id=optimization_id,
            decision_id=decision_id,
            requester=requester,
            approver=None,
            status=ApprovalStatus.PENDING,
            reason=reason,
            context=context,
            expires_at=expires_at
        )
        
        self._requests[request_id] = request
        logger.info(f"Approval request created: {request_id}")
        return request
    
    def approve(self, request_id: str, approver: str) -> Optional[ApprovalRequest]:
        """Approve request"""
        request = self._requests.get(request_id)
        if not request or request.status != ApprovalStatus.PENDING:
            return None
        
        if datetime.now() > datetime.fromisoformat(request.expires_at):
            request.status = ApprovalStatus.EXPIRED
            return None
        
        request.status = ApprovalStatus.APPROVED
        request.approver = approver
        request.decided_at = datetime.now().isoformat()
        
        logger.info(f"Approval request approved: {request_id} by {approver}")
        return request
    
    def reject(self, request_id: str, approver: str, reason: str) -> Optional[ApprovalRequest]:
        """Reject request"""
        request = self._requests.get(request_id)
        if not request or request.status != ApprovalStatus.PENDING:
            return None
        
        request.status = ApprovalStatus.REJECTED
        request.approver = approver
        request.reason = reason
        request.decided_at = datetime.now().isoformat()
        
        logger.info(f"Approval request rejected: {request_id} by {approver}")
        return request
    
    def get_pending_requests(self) -> List[ApprovalRequest]:
        """Get pending approval requests"""
        return [r for r in self._requests.values() if r.status == ApprovalStatus.PENDING]


from datetime import timedelta


def main():
    print("Approval Workflow loaded")


if __name__ == "__main__":
    main()
