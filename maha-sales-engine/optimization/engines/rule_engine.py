#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Rule Engine
Evaluates optimization rules and triggers optimizations.
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

logger = logging.getLogger("maha-sales-engine.optimization.rule")


class RuleType(Enum):
    THRESHOLD = "threshold"
    TREND = "trend"
    ANOMALY = "anomaly"
    COMPARATIVE = "comparative"


class RuleStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"


@dataclass
class OptimizationRule:
    rule_id: str
    name: str
    description: str
    rule_type: RuleType
    category: str
    target_metric: str
    condition: Dict[str, Any]
    action: Dict[str, Any]
    priority: int
    status: RuleStatus
    cooldown_minutes: int
    last_triggered_at: Optional[str] = None
    trigger_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class RuleEngine:
    """
    Rule engine that evaluates optimization rules.
    """
    
    def __init__(self, db_manager):
        self.db = db_manager
        self._rules: Dict[str, OptimizationRule] = {}
        self._load_default_rules()
    
    def _load_default_rules(self):
        """Load default optimization rules"""
        default_rules = [
            OptimizationRule(
                rule_id="rule-001",
                name="Low Conversion Rate",
                description="Trigger when conversion rate drops below 2%",
                rule_type=RuleType.THRESHOLD,
                category="conversion",
                target_metric="conversion_rate",
                condition={"operator": "<", "value": 0.02},
                action={"optimizer": "marketing_optimizer", "action": "optimize_ctr"},
                priority=1,
                status=RuleStatus.ACTIVE,
                cooldown_minutes=60
            ),
            OptimizationRule(
                rule_id="rule-002",
                name="High Refund Rate",
                description="Trigger when refund rate exceeds 5%",
                rule_type=RuleType.THRESHOLD,
                category="retention",
                target_metric="refund_rate",
                condition={"operator": ">", "value": 0.05},
                action={"optimizer": "customer_retention", "action": "reduce_refunds"},
                priority=1,
                status=RuleStatus.ACTIVE,
                cooldown_minutes=120
            ),
            OptimizationRule(
                rule_id="rule-003",
                name="Declining Traffic",
                description="Trigger when organic traffic declines for 3 consecutive days",
                rule_type=RuleType.TREND,
                category="traffic",
                target_metric="organic_traffic",
                condition={"operator": "declining", "periods": 3},
                action={"optimizer": "seo_optimizer", "action": "optimize_seo"},
                priority=2,
                status=RuleStatus.ACTIVE,
                cooldown_minutes=1440
            ),
            OptimizationRule(
                rule_id="rule-004",
                name="Price Opportunity",
                description="Trigger when competitor price is significantly lower",
                rule_type=RuleType.COMPARATIVE,
                category="pricing",
                target_metric="competitor_price_delta",
                condition={"operator": "<", "value": -0.1},
                action={"optimizer": "pricing_engine", "action": "review_pricing"},
                priority=3,
                status=RuleStatus.ACTIVE,
                cooldown_minutes=360
            )
        ]
        
        for rule in default_rules:
            self._rules[rule.rule_id] = rule
    
    def evaluate_rules(self, metrics: Dict[str, Any]) -> List[OptimizationRule]:
        """Evaluate all active rules against current metrics"""
        triggered = []
        
        for rule in self._rules.values():
            if rule.status != RuleStatus.ACTIVE:
                continue
            
            if self._is_on_cooldown(rule):
                continue
            
            if self._evaluate_condition(rule.condition, metrics, rule.target_metric):
                rule.last_triggered_at = datetime.now().isoformat()
                rule.trigger_count += 1
                triggered.append(rule)
                logger.info(f"Rule triggered: {rule.rule_id} - {rule.name}")
        
        return triggered
    
    def _is_on_cooldown(self, rule: OptimizationRule) -> bool:
        """Check if rule is on cooldown"""
        if not rule.last_triggered_at:
            return False
        
        last_triggered = datetime.fromisoformat(rule.last_triggered_at)
        cooldown = datetime.now() - last_triggered
        return cooldown.total_seconds() < (rule.cooldown_minutes * 60)
    
    def _evaluate_condition(self, condition: Dict[str, Any], metrics: Dict[str, Any], target_metric: str = None) -> bool:
        """Evaluate rule condition"""
        operator = condition.get("operator")
        target_metric = condition.get("target_metric", target_metric)
        value = condition.get("value")
        
        if target_metric:
            actual = metrics.get(target_metric)
            if actual is None:
                return False
            
            if operator == "<":
                return actual < value
            elif operator == ">":
                return actual > value
            elif operator == "==":
                return actual == value
            elif operator == "<=":
                return actual <= value
            elif operator == ">=":
                return actual >= value
            elif operator == "declining":
                # Check trend
                history = metrics.get(f"{target_metric}_history", [])
                if len(history) < condition.get("periods", 3):
                    return False
                return all(history[i] > history[i+1] for i in range(len(history)-1))
        
        return False
    
    def get_rules(self) -> List[OptimizationRule]:
        """Get all rules"""
        return list(self._rules.values())


def main():
    print("Rule Engine loaded")


if __name__ == "__main__":
    main()
