#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Rules Engine
Configurable business rules for automation.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.sales-automation.rules")


@dataclass
class Rule:
    rule_id: str
    name: str
    description: str
    condition: Dict[str, Any]
    action: Dict[str, Any]
    priority: int
    enabled: bool
    created_at: str


class RulesEngine:
    """Evaluate configurable business rules"""
    
    def __init__(self, db_manager, event_bus):
        self.db = db_manager
        self.event_bus = event_bus
        self._cache: Dict[str, Rule] = {}
    
    def add_rule(self, name: str, description: str, condition: Dict[str, Any],
                 action: Dict[str, Any], priority: int = 100) -> Optional[str]:
        try:
            rule_id = f"rule-{uuid.uuid4().hex[:12]}"
            now = datetime.now().isoformat()
            
            rule = Rule(
                rule_id=rule_id,
                name=name,
                description=description,
                condition=condition,
                action=action,
                priority=priority,
                enabled=True,
                created_at=now
            )
            
            self._save_rule(rule)
            self._cache[rule_id] = rule
            
            logger.info(f"Rule added: {rule_id} - {name}")
            return rule_id
        except Exception as e:
            logger.error(f"Failed to add rule: {e}")
            return None
    
    def evaluate(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        results = []
        rules = self._get_enabled_rules()
        
        for rule in sorted(rules, key=lambda r: r.priority):
            if self._evaluate_condition(rule.condition, context):
                results.append({
                    "rule_id": rule.rule_id,
                    "name": rule.name,
                    "action": rule.action,
                    "matched": True
                })
        
        return results
    
    def validate_publication(self, marketplace_id: str, product_id: str, 
                            product_data: Dict[str, Any]) -> Dict[str, Any]:
        context = {
            "marketplace_id": marketplace_id,
            "product_id": product_id,
            "product_data": product_data
        }
        
        rules = self.evaluate(context)
        blocking_rules = [r for r in rules if r["action"].get("block", False)]
        
        if blocking_rules:
            return {
                "valid": False,
                "error": f"Blocked by rules: {[r['name'] for r in blocking_rules]}",
                "rules": blocking_rules
            }
        
        return {"valid": True, "rules": rules}
    
    def requires_approval(self, marketplace_id: str, product_id: str) -> bool:
        context = {"marketplace_id": marketplace_id, "product_id": product_id}
        rules = self.evaluate(context)
        return any(r["action"].get("require_approval", False) for r in rules)
    
    def _evaluate_condition(self, condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        try:
            field = condition.get("field", "")
            operator = condition.get("operator", "eq")
            value = condition.get("value")
            
            context_value = context.get(field)
            
            if operator == "eq":
                return context_value == value
            elif operator == "neq":
                return context_value != value
            elif operator == "gt":
                return context_value > value
            elif operator == "lt":
                return context_value < value
            elif operator == "gte":
                return context_value >= value
            elif operator == "lte":
                return context_value <= value
            elif operator == "in":
                return context_value in value
            elif operator == "contains":
                return value in str(context_value)
            elif operator == "exists":
                return context_value is not None
            
            return False
        except Exception:
            return False
    
    def _get_enabled_rules(self) -> List[Rule]:
        rules = []
        for rule in self._cache.values():
            if rule.enabled:
                rules.append(rule)
        return rules
    
    def _save_rule(self, rule: Rule):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO rules (rule_id, name, description, condition, action, priority, enabled, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rule.rule_id, rule.name, rule.description,
                json.dumps(rule.condition), json.dumps(rule.action),
                rule.priority, rule.enabled, rule.created_at
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to save rule: {e}")


def main():
    print("Rules Engine initialized")


if __name__ == "__main__":
    main()
