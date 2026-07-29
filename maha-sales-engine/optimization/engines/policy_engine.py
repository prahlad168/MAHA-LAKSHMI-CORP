#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Policy Engine
Validates optimizations against business, risk, compliance, marketplace, and financial policies.
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

logger = logging.getLogger("maha-sales-engine.optimization.policy")


class PolicyType(Enum):
    BUSINESS = "business"
    RISK = "risk"
    COMPLIANCE = "compliance"
    MARKETPLACE = "marketplace"
    FINANCIAL = "financial"


class PolicyResult(Enum):
    ALLOWED = "allowed"
    DENIED = "denied"
    REQUIRES_APPROVAL = "requires_approval"


@dataclass
class Policy:
    policy_id: str
    name: str
    policy_type: PolicyType
    description: str
    rules: List[Dict[str, Any]]
    active: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class PolicyEvaluation:
    evaluation_id: str
    policy_id: str
    optimization_id: str
    result: PolicyResult
    reason: str
    details: Dict[str, Any] = field(default_factory=dict)
    evaluated_at: str = field(default_factory=lambda: datetime.now().isoformat())


class PolicyEngine:
    """
    Policy engine that validates optimizations against configured policies.
    No optimization may bypass the policy engine.
    """
    
    def __init__(self, db_manager):
        self.db = db_manager
        self._policies: Dict[str, Policy] = {}
        self._load_default_policies()
    
    def _load_default_policies(self):
        """Load default policies"""
        default_policies = [
            Policy(
                policy_id="pol-001",
                name="Maximum Price Change",
                policy_type=PolicyType.BUSINESS,
                description="Price changes cannot exceed 50%",
                rules=[{"field": "price_change_percent", "operator": "<=", "value": 50}]
            ),
            Policy(
                policy_id="pol-002",
                name="High Risk Approval",
                policy_type=PolicyType.RISK,
                description="Risk score above 0.8 requires approval",
                rules=[{"field": "risk_score", "operator": "<=", "value": 0.8}]
            ),
            Policy(
                policy_id="pol-003",
                name="Autonomous Mode Limit",
                policy_type=PolicyType.FINANCIAL,
                description="Autonomous mode only for optimizations under $1000 expected impact",
                rules=[{"field": "expected_revenue_impact", "operator": "<=", "value": 1000}]
            ),
            Policy(
                policy_id="pol-004",
                name="Marketplace Compliance",
                policy_type=PolicyType.MARKETPLACE,
                description="Must comply with marketplace terms of service",
                rules=[{"field": "marketplace_compliant", "operator": "==", "value": True}]
            ),
            Policy(
                policy_id="pol-005",
                name="Minimum Confidence",
                policy_type=PolicyType.BUSINESS,
                description="Confidence must be above 60%",
                rules=[{"field": "confidence", "operator": ">=", "value": 0.6}]
            )
        ]
        
        for policy in default_policies:
            self._policies[policy.policy_id] = policy
    
    def evaluate(self, optimization_context: OptimizationContext, data: Dict[str, Any]) -> PolicyEvaluation:
        """
        Evaluate optimization against all active policies.
        Returns evaluation result.
        """
        evaluation_id = f"eval-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
        violations = []
        requires_approval = False
        
        for policy in self._policies.values():
            if not policy.active:
                continue
            
            result, reason, details = self._evaluate_policy(policy, data)
            if result == PolicyResult.DENIED:
                violations.append(f"{policy.name}: {reason}")
            elif result == PolicyResult.REQUIRES_APPROVAL:
                requires_approval = True
        
        if violations:
            result = PolicyResult.DENIED
            reason = "; ".join(violations)
        elif requires_approval:
            result = PolicyResult.REQUIRES_APPROVAL
            reason = "One or more policies require approval"
        else:
            result = PolicyResult.ALLOWED
            reason = "All policies passed"
        
        evaluation = PolicyEvaluation(
            evaluation_id=evaluation_id,
            policy_id="multiple",
            optimization_id=optimization_context.optimization_id,
            result=result,
            reason=reason,
            details={"policies_checked": len(self._policies), "violations": violations}
        )
        
        logger.info(f"Policy evaluation {evaluation_id}: {result.value} for {optimization_context.optimization_id}")
        return evaluation
    
    def _evaluate_policy(self, policy: Policy, data: Dict[str, Any]) -> tuple:
        """Evaluate single policy"""
        for rule in policy.rules:
            field = rule["field"]
            operator = rule["operator"]
            value = rule["value"]
            
            actual = data.get(field)
            if actual is None:
                return PolicyResult.DENIED, f"Missing field: {field}", {}
            
            if operator == "<=" and actual > value:
                return PolicyResult.DENIED, f"{field} ({actual}) exceeds maximum ({value})", {}
            elif operator == ">=" and actual < value:
                return PolicyResult.DENIED, f"{field} ({actual}) below minimum ({value})", {}
            elif operator == "==" and actual != value:
                return PolicyResult.DENIED, f"{field} ({actual}) does not match required ({value})", {}
            elif operator == "!=" and actual == value:
                return PolicyResult.DENIED, f"{field} ({actual}) matches forbidden value ({value})", {}
        
        # Check if policy requires approval
        if policy.policy_type == PolicyType.RISK and data.get("risk_score", 0) > 0.8:
            return PolicyResult.REQUIRES_APPROVAL, "Risk score above threshold", {}
        
        return PolicyResult.ALLOWED, "Policy passed", {}
    
    def add_policy(self, policy: Policy):
        """Add new policy"""
        self._policies[policy.policy_id] = policy
        logger.info(f"Policy added: {policy.policy_id}")
    
    def get_policies(self) -> List[Policy]:
        """Get all policies"""
        return list(self._policies.values())


def main():
    print("Policy Engine loaded")


if __name__ == "__main__":
    main()
