#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Decision Engine
Makes optimization decisions with evidence, confidence, risk, and rollback plans.
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

logger = logging.getLogger("maha-sales-engine.optimization.decision")


class DecisionStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    FAILED = "failed"


@dataclass
class Decision:
    decision_id: str
    optimization_id: str
    reason: str
    evidence: Dict[str, Any]
    confidence: float
    risk_score: float
    expected_impact: Dict[str, float]
    rollback_plan: Dict[str, Any]
    related_metrics: List[str]
    status: DecisionStatus
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    decided_at: Optional[str] = None
    decided_by: Optional[str] = None


class DecisionEngine:
    """
    Decision engine that creates optimization decisions.
    Every decision includes reason, evidence, confidence, risk, expected impact, and rollback plan.
    """
    
    def __init__(self, db_manager, confidence_engine, risk_engine, simulation_engine):
        self.db = db_manager
        self.confidence_engine = confidence_engine
        self.risk_engine = risk_engine
        self.simulation_engine = simulation_engine
        self._decisions: Dict[str, Decision] = {}
    
    def create_decision(self, optimization_context, optimizer_result, simulation_result) -> Decision:
        """Create optimization decision"""
        decision_id = f"dec-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
        
        confidence = self.confidence_engine.calculate(optimization_context, optimizer_result)
        risk_assessment = self.risk_engine.assess(optimization_context, optimizer_result)
        
        decision = Decision(
            decision_id=decision_id,
            optimization_id=optimization_context.optimization_id,
            reason=optimizer_result.get("reason", "Optimization opportunity identified"),
            evidence=optimizer_result.get("evidence", {}),
            confidence=confidence,
            risk_score=risk_assessment.risk_score,
            expected_impact=simulation_result.get("expected_impact", {}),
            rollback_plan=simulation_result.get("rollback_plan", {}),
            related_metrics=simulation_result.get("related_metrics", []),
            status=DecisionStatus.PENDING
        )
        
        self._decisions[decision_id] = decision
        logger.info(f"Decision created: {decision_id} with confidence {confidence:.2f}")
        return decision
    
    def approve_decision(self, decision_id: str, approved_by: str) -> Optional[Decision]:
        """Approve decision"""
        decision = self._decisions.get(decision_id)
        if not decision:
            return None
        
        decision.status = DecisionStatus.APPROVED
        decision.decided_at = datetime.now().isoformat()
        decision.decided_by = approved_by
        
        logger.info(f"Decision approved: {decision_id} by {approved_by}")
        return decision
    
    def reject_decision(self, decision_id: str, rejected_by: str, reason: str) -> Optional[Decision]:
        """Reject decision"""
        decision = self._decisions.get(decision_id)
        if not decision:
            return None
        
        decision.status = DecisionStatus.REJECTED
        decision.decided_at = datetime.now().isoformat()
        decision.decided_by = rejected_by
        decision.reason = reason
        
        logger.info(f"Decision rejected: {decision_id} by {rejected_by}")
        return decision


def main():
    print("Decision Engine loaded")


if __name__ == "__main__":
    main()
