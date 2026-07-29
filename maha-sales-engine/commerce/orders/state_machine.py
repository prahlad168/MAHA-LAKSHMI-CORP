#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Order State Machine
Order lifecycle state management.
"""

import logging
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger("maha-sales-engine.commerce.orders")


class OrderStatus(Enum):
    DRAFT = "draft"
    PENDING_PAYMENT = "pending_payment"
    AUTHORIZED = "authorized"
    PAID = "paid"
    DELIVERING = "delivering"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    REFUND_REQUESTED = "refund_requested"
    REFUNDED = "refunded"
    FAILED = "failed"


class OrderStateMachine:
    """State machine for order lifecycle"""
    
    VALID_TRANSITIONS = {
        OrderStatus.DRAFT.value: [
            OrderStatus.PENDING_PAYMENT.value,
            OrderStatus.CANCELLED.value
        ],
        OrderStatus.PENDING_PAYMENT.value: [
            OrderStatus.AUTHORIZED.value,
            OrderStatus.PAID.value,
            OrderStatus.CANCELLED.value,
            OrderStatus.EXPIRED.value,
            OrderStatus.FAILED.value
        ],
        OrderStatus.AUTHORIZED.value: [
            OrderStatus.PAID.value,
            OrderStatus.CANCELLED.value,
            OrderStatus.FAILED.value
        ],
        OrderStatus.PAID.value: [
            OrderStatus.DELIVERING.value,
            OrderStatus.REFUND_REQUESTED.value,
            OrderStatus.FAILED.value
        ],
        OrderStatus.DELIVERING.value: [
            OrderStatus.DELIVERED.value,
            OrderStatus.FAILED.value
        ],
        OrderStatus.DELIVERED.value: [
            OrderStatus.COMPLETED.value,
            OrderStatus.REFUND_REQUESTED.value
        ],
        OrderStatus.COMPLETED.value: [
            OrderStatus.REFUND_REQUESTED.value
        ],
        OrderStatus.CANCELLED.value: [],
        OrderStatus.EXPIRED.value: [],
        OrderStatus.REFUND_REQUESTED.value: [
            OrderStatus.REFUNDED.value,
            OrderStatus.DELIVERED.value,
            OrderStatus.COMPLETED.value
        ],
        OrderStatus.REFUNDED.value: [],
        OrderStatus.FAILED.value: [
            OrderStatus.PENDING_PAYMENT.value,
            OrderStatus.DRAFT.value
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


class OrderStatusManager:
    """Manage order status transitions"""
    
    def __init__(self):
        self.state_machine = OrderStateMachine()
    
    def transition(self, order: Dict[str, any], new_status: str) -> Dict[str, any]:
        current_status = order.get("status", OrderStatus.DRAFT.value)
        
        validation = self.state_machine.validate_transition(current_status, new_status)
        if not validation["valid"]:
            return {
                "success": False,
                "error": validation["error"],
                "current_status": current_status,
                "attempted_status": new_status
            }
        
        old_status = order.get("status")
        order["status"] = new_status
        
        logger.info(f"Order status transition: {old_status} -> {new_status}")
        
        return {
            "success": True,
            "old_status": old_status,
            "new_status": new_status,
            "order": order
        }
    
    def can_pay(self, order: Dict[str, any]) -> bool:
        current_status = order.get("status", OrderStatus.DRAFT.value)
        valid_targets = self.state_machine.get_valid_transitions(current_status)
        return OrderStatus.PAID.value in valid_targets or OrderStatus.AUTHORIZED.value in valid_targets
    
    def can_refund(self, order: Dict[str, any]) -> bool:
        current_status = order.get("status", OrderStatus.DRAFT.value)
        valid_targets = self.state_machine.get_valid_transitions(current_status)
        return OrderStatus.REFUND_REQUESTED.value in valid_targets


def main():
    sm = OrderStateMachine()
    print("Order State Machine initialized")
    print(f"Valid transitions from draft: {sm.get_valid_transitions('draft')}")


if __name__ == "__main__":
    main()
