#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Payment Router
Route payments to appropriate providers based on rules.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.commerce.payments.router")


class PaymentRouter:
    """Route payments to appropriate providers"""
    
    def __init__(self, db_manager, provider_registry):
        self.db = db_manager
        self.provider_registry = provider_registry
        self._rules: List[Dict[str, Any]] = []
    
    def add_rule(self, rule: Dict[str, Any]):
        self._rules.append(rule)
        logger.info(f"Payment routing rule added: {rule.get('name', 'unnamed')}")
    
    def route(self, payment_request: Dict[str, Any]) -> Optional[str]:
        try:
            for rule in sorted(self._rules, key=lambda r: r.get("priority", 100)):
                if self._matches(payment_request, rule):
                    provider_name = rule.get("provider")
                    if self.provider_registry.get_provider(provider_name):
                        return provider_name
            
            return None
        except Exception as e:
            logger.error(f"Payment routing failed: {e}")
            return None
    
    def _matches(self, request: Dict[str, Any], rule: Dict[str, Any]) -> bool:
        conditions = rule.get("conditions", {})
        
        for field, condition in conditions.items():
            request_value = request.get(field)
            operator = condition.get("operator", "eq")
            expected = condition.get("value")
            
            if operator == "eq" and request_value != expected:
                return False
            elif operator == "in" and request_value not in expected:
                return False
            elif operator == "contains" and expected not in str(request_value):
                return False
        
        return True


def main():
    print("Payment Router initialized")


if __name__ == "__main__":
    main()
