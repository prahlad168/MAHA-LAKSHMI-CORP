#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Automation State Machine
State machine for sales automation lifecycle.
"""

import logging
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger("maha-sales-engine.sales-automation.state_machine")


class AutomationStatus(Enum):
    DRAFT = "draft"
    READY = "ready"
    SCHEDULED = "scheduled"
    QUEUED = "queued"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    VERIFYING = "verifying"
    SYNCHRONIZING = "synchronizing"
    RETRYING = "retrying"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    FAILED = "failed"


class AutomationStateMachine:
    """State machine for sales automation"""
    
    VALID_TRANSITIONS = {
        AutomationStatus.DRAFT.value: [
            AutomationStatus.READY.value,
            AutomationStatus.QUEUED.value,
            AutomationStatus.SCHEDULED.value,
            AutomationStatus.FAILED.value
        ],
        AutomationStatus.READY.value: [
            AutomationStatus.QUEUED.value,
            AutomationStatus.SCHEDULED.value,
            AutomationStatus.DRAFT.value,
            AutomationStatus.FAILED.value,
            AutomationStatus.PUBLISHING.value
        ],
        AutomationStatus.SCHEDULED.value: [
            AutomationStatus.QUEUED.value,
            AutomationStatus.READY.value,
            AutomationStatus.CANCELLED.value,
            AutomationStatus.FAILED.value
        ],
        AutomationStatus.QUEUED.value: [
            AutomationStatus.PUBLISHING.value,
            AutomationStatus.PAUSED.value,
            AutomationStatus.CANCELLED.value
        ],
        AutomationStatus.PUBLISHING.value: [
            AutomationStatus.PUBLISHED.value,
            AutomationStatus.VERIFYING.value,
            AutomationStatus.FAILED.value,
            AutomationStatus.RETRYING.value
        ],
        AutomationStatus.PUBLISHED.value: [
            AutomationStatus.VERIFYING.value,
            AutomationStatus.SYNCHRONIZING.value,
            AutomationStatus.FAILED.value
        ],
        AutomationStatus.VERIFYING.value: [
            AutomationStatus.SYNCHRONIZING.value,
            AutomationStatus.PUBLISHED.value,
            AutomationStatus.FAILED.value
        ],
        AutomationStatus.SYNCHRONIZING.value: [
            AutomationStatus.COMPLETED.value,
            AutomationStatus.PUBLISHED.value,
            AutomationStatus.FAILED.value
        ],
        AutomationStatus.RETRYING.value: [
            AutomationStatus.PUBLISHING.value,
            AutomationStatus.FAILED.value,
            AutomationStatus.QUEUED.value
        ],
        AutomationStatus.PAUSED.value: [
            AutomationStatus.QUEUED.value,
            AutomationStatus.CANCELLED.value
        ],
        AutomationStatus.CANCELLED.value: [],
        AutomationStatus.COMPLETED.value: [
            AutomationStatus.ARCHIVED.value
        ],
        AutomationStatus.ARCHIVED.value: [],
        AutomationStatus.FAILED.value: [
            AutomationStatus.RETRYING.value,
            AutomationStatus.QUEUED.value,
            AutomationStatus.DRAFT.value,
            AutomationStatus.READY.value
        ]
    }
    
    @classmethod
    def can_transition(cls, from_status: str, to_status: str) -> bool:
        valid_targets = cls.VALID_TRANSITIONS.get(from_status, [])
        return to_status in valid_targets
    
    @classmethod
    def get_valid_transitions(cls, from_status: str) -> List[str]:
        return cls.VALID_TRANSITIONS.get(from_status, [])
    
    @classmethod
    def validate_transition(cls, from_status: str, to_status: str) -> Dict[str, any]:
        valid = cls.can_transition(from_status, to_status)
        return {
            "valid": valid,
            "from_status": from_status,
            "to_status": to_status,
            "valid_targets": cls.get_valid_transitions(from_status),
            "error": None if valid else f"Invalid transition from {from_status} to {to_status}"
        }


class AutomationStatusManager:
    """Manage automation status transitions"""
    
    def __init__(self):
        self.state_machine = AutomationStateMachine()
    
    def transition(self, record: Dict[str, any], new_status: str) -> Dict[str, any]:
        current_status = record.get("status", AutomationStatus.DRAFT.value)
        
        validation = self.state_machine.validate_transition(current_status, new_status)
        if not validation["valid"]:
            return {
                "success": False,
                "error": validation["error"],
                "current_status": current_status,
                "attempted_status": new_status
            }
        
        old_status = record.get("status")
        record["status"] = new_status
        
        logger.info(f"Status transition: {old_status} -> {new_status}")
        
        return {
            "success": True,
            "old_status": old_status,
            "new_status": new_status,
            "record": record
        }
    
    def can_publish(self, record: Dict[str, any]) -> bool:
        current_status = record.get("status", AutomationStatus.DRAFT.value)
        valid_targets = self.state_machine.get_valid_transitions(current_status)
        return AutomationStatus.PUBLISHING.value in valid_targets
    
    def can_retry(self, record: Dict[str, any]) -> bool:
        current_status = record.get("status", AutomationStatus.DRAFT.value)
        valid_targets = self.state_machine.get_valid_transitions(current_status)
        return AutomationStatus.RETRYING.value in valid_targets


def main():
    sm = AutomationStateMachine()
    print("Automation State Machine initialized")
    print(f"Valid transitions from draft: {sm.get_valid_transitions('draft')}")


if __name__ == "__main__":
    main()
