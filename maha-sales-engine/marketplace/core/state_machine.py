#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Marketplace State Machine
Publication status state machine with transition validation.
"""

import logging
from typing import Any, Dict, List, Optional
from enum import Enum

logger = logging.getLogger("maha-sales-engine.marketplace.state_machine")


class PublicationStatus(Enum):
    DRAFT = "draft"
    PREPARING = "preparing"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    UPDATING = "updating"
    ARCHIVED = "archived"
    DELETED = "deleted"
    SYNCING = "syncing"
    FAILED = "failed"
    RETRYING = "retrying"


class StateMachine:
    """State machine for publication status transitions"""
    
    VALID_TRANSITIONS = {
        PublicationStatus.DRAFT.value: [
            PublicationStatus.PREPARING.value,
            PublicationStatus.PUBLISHING.value,
            PublicationStatus.FAILED.value
        ],
        PublicationStatus.PREPARING.value: [
            PublicationStatus.PUBLISHING.value,
            PublicationStatus.DRAFT.value,
            PublicationStatus.FAILED.value
        ],
        PublicationStatus.PUBLISHING.value: [
            PublicationStatus.PUBLISHED.value,
            PublicationStatus.FAILED.value,
            PublicationStatus.RETRYING.value
        ],
        PublicationStatus.PUBLISHED.value: [
            PublicationStatus.UPDATING.value,
            PublicationStatus.ARCHIVED.value,
            PublicationStatus.SYNCING.value,
            PublicationStatus.FAILED.value
        ],
        PublicationStatus.UPDATING.value: [
            PublicationStatus.PUBLISHED.value,
            PublicationStatus.FAILED.value,
            PublicationStatus.RETRYING.value
        ],
        PublicationStatus.ARCHIVED.value: [
            PublicationStatus.PUBLISHING.value,
            PublicationStatus.DRAFT.value
        ],
        PublicationStatus.DELETED.value: [],
        PublicationStatus.SYNCING.value: [
            PublicationStatus.PUBLISHED.value,
            PublicationStatus.FAILED.value
        ],
        PublicationStatus.FAILED.value: [
            PublicationStatus.RETRYING.value,
            PublicationStatus.PREPARING.value,
            PublicationStatus.DRAFT.value,
            PublicationStatus.FAILED.value
        ],
        PublicationStatus.RETRYING.value: [
            PublicationStatus.PUBLISHING.value,
            PublicationStatus.FAILED.value,
            PublicationStatus.DRAFT.value
        ]
    }
    
    @classmethod
    def can_transition(cls, from_status: str, to_status: str) -> bool:
        """Check if transition is valid"""
        if from_status not in cls.VALID_TRANSITIONS:
            return False
        return to_status in cls.VALID_TRANSITIONS[from_status]
    
    @classmethod
    def get_valid_transitions(cls, from_status: str) -> List[str]:
        """Get valid target statuses"""
        return cls.VALID_TRANSITIONS.get(from_status, [])
    
    @classmethod
    def validate_transition(cls, from_status: str, to_status: str) -> Dict[str, Any]:
        """Validate and return transition details"""
        valid = cls.can_transition(from_status, to_status)
        valid_targets = cls.get_valid_transitions(from_status)
        
        return {
            "valid": valid,
            "from_status": from_status,
            "to_status": to_status,
            "valid_targets": valid_targets,
            "error": None if valid else f"Invalid transition from {from_status} to {to_status}. Valid targets: {valid_targets}"
        }
    
    @classmethod
    def get_terminal_statuses(cls) -> List[str]:
        """Get terminal statuses (no outgoing transitions)"""
        return [status for status, targets in cls.VALID_TRANSITIONS.items() if not targets]
    
    @classmethod
    def get_initial_statuses(cls) -> List[str]:
        """Get initial statuses (valid starting points)"""
        return [PublicationStatus.DRAFT.value, PublicationStatus.FAILED.value]


class StatusManager:
    """Manage publication status with state machine validation."""
    
    def __init__(self):
        self.state_machine = StateMachine()
    
    def transition(self, mapping: Dict[str, Any], new_status: str) -> Dict[str, Any]:
        current_status = mapping.get("publication_status", PublicationStatus.DRAFT.value)
        validation = self.state_machine.validate_transition(current_status, new_status)
        if not validation["valid"]:
            return {"success": False, "error": validation["error"], "current_status": current_status, "attempted_status": new_status}
        old_status = mapping.get("publication_status")
        mapping["publication_status"] = new_status
        logger.info("Status transition: %s -> %s", old_status, new_status)
        return {"success": True, "old_status": old_status, "new_status": new_status, "mapping": mapping}

    def can_publish(self, mapping: Dict[str, Any]) -> bool:
        current_status = mapping.get("publication_status", PublicationStatus.DRAFT.value)
        return PublicationStatus.PUBLISHING.value in self.state_machine.get_valid_transitions(current_status)

    def can_update(self, mapping: Dict[str, Any]) -> bool:
        current_status = mapping.get("publication_status", PublicationStatus.DRAFT.value)
        return PublicationStatus.UPDATING.value in self.state_machine.get_valid_transitions(current_status)

    def can_archive(self, mapping: Dict[str, Any]) -> bool:
        current_status = mapping.get("publication_status", PublicationStatus.DRAFT.value)
        return PublicationStatus.ARCHIVED.value in self.state_machine.get_valid_transitions(current_status)

    def can_delete(self, mapping: Dict[str, Any]) -> bool:
        current_status = mapping.get("publication_status", PublicationStatus.DRAFT.value)
        return PublicationStatus.DELETED.value in self.state_machine.get_valid_transitions(current_status)


def main():
    """Test state machine"""
    sm = StateMachine()
    manager = StatusManager()
    mapping = {"publication_status": PublicationStatus.DRAFT.value}
    result = manager.transition(mapping, PublicationStatus.PUBLISHING.value)
    print(f"Draft -> Publishing: {result['success']}")
    mapping = {"publication_status": PublicationStatus.DRAFT.value}
    result = manager.transition(mapping, PublicationStatus.DELETED.value)
    print(f"Draft -> Deleted: {result['success']}")
    mapping = {"publication_status": PublicationStatus.PUBLISHED.value}
    valid = sm.get_valid_transitions(PublicationStatus.PUBLISHED.value)
    print(f"Valid from Published: {valid}")


if __name__ == "__main__":
    main()
