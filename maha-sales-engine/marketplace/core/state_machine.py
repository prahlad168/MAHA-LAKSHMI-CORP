#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Marketplace State Machine
Publication status state machine with transition validation.
"""

import logging
from enum import Enum
from typing import Any, Dict, List, Optional

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


# Backward-compatible name used by the legacy marketplace API/tests.
StatusManager = StateMachine
