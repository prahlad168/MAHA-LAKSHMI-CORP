#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Policy Engine
Centralized operational policies.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.sales-automation.policy")


@dataclass
class Policy:
    policy_id: str
    name: str
    policy_type: str
    description: str
    rules: Dict[str, Any]
    enabled: bool
    created_at: str
    updated_at: str


class PolicyEngine:
    """Manage operational policies"""
    
    POLICY_TYPES = [
        "publishing",
        "retry",
        "approval",
        "notification",
        "marketplace",
        "scheduling",
        "security",
        "compliance"
    ]
    
    def __init__(self, db_manager):
        self.db = db_manager
        self._cache: Dict[str, Policy] = {}
    
    def create_policy(self, name: str, policy_type: str, description: str,
                     rules: Dict[str, Any]) -> Optional[str]:
        try:
            policy_id = f"pol-{uuid.uuid4().hex[:12]}"
            now = datetime.now().isoformat()
            
            policy = Policy(
                policy_id=policy_id,
                name=name,
                policy_type=policy_type,
                description=description,
                rules=rules,
                enabled=True,
                created_at=now,
                updated_at=now
            )
            
            self._save_policy(policy)
            self._cache[policy_id] = policy
            
            logger.info(f"Policy created: {policy_id} - {name}")
            return policy_id
        except Exception as e:
            logger.error(f"Failed to create policy: {e}")
            return None
    
    def get_policy(self, policy_type: str) -> Optional[Policy]:
        for policy in self._cache.values():
            if policy.policy_type == policy_type and policy.enabled:
                return policy
        return None
    
    def evaluate(self, policy_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        policy = self.get_policy(policy_type)
        if not policy:
            return {"allowed": True, "policy": None}
        
        rules = policy.rules
        allowed = rules.get("allowed", True)
        
        return {
            "allowed": allowed,
            "policy": policy.name,
            "rules": rules,
            "context": context
        }
    
    def _save_policy(self, policy: Policy):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO policies 
                (policy_id, name, policy_type, description, rules, enabled, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                policy.policy_id, policy.name, policy.policy_type,
                policy.description, json.dumps(policy.rules),
                policy.enabled, policy.created_at, policy.updated_at
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to save policy: {e}")


def main():
    print("Policy Engine initialized")


if __name__ == "__main__":
    main()
