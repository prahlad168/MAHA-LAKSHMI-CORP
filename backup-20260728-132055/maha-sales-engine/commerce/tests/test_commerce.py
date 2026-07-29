#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Commerce Tests
Test suite for commerce platform.
"""

import os
import sys
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from orders.state_machine import OrderStateMachine, OrderStatus, OrderStatusManager
from customers.engine import CustomerEngine
from orders.engine import OrderEngine
from licenses.engine import LicenseEngine
from delivery.engine import DigitalDeliveryEngine
from cart.engine import CartEngine
from checkout.engine import CheckoutEngine
from coupons.engine import CouponEngine
from promotions.engine import PromotionEngine
from tax.engine import TaxEngine
from refunds.engine import RefundEngine
from wallets.engine import WalletEngine
from payouts.engine import PayoutEngine
from fraud.engine import FraudDetectionEngine


# ============ FIXTURES ============

@pytest.fixture
def temp_dir():
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def db_manager(temp_dir):
    from core.engine import DatabaseManager
    db_path = temp_dir / "test.db"
    return DatabaseManager(db_path)


@pytest.fixture
def mock_event_bus():
    return Mock()


# ============ STATE MACHINE TESTS ============

class TestOrderStateMachine:
    def test_valid_transitions(self):
        assert OrderStateMachine.can_transition("draft", "pending_payment") is True
        assert OrderStateMachine.can_transition("draft", "completed") is False
    
    def test_status_manager_transition(self):
        manager = OrderStatusManager()
        order = {"status": "draft"}
        result = manager.transition(order, "pending_payment")
        assert result["success"] is True
        assert order["status"] == "pending_payment"
    
    def test_can_pay(self):
        manager = OrderStatusManager()
        order = {"status": "pending_payment"}
        assert manager.can_pay(order) is True


# ============ CUSTOMER TESTS ============

class TestCustomerEngine:
    def test_create_customer(self, db_manager):
        engine = CustomerEngine(db_manager)
        customer_id = engine.create_customer("test@example.com", "Test User")
        assert customer_id is not None
        assert customer_id.startswith("cust-")
    
    def test_get_customer(self, db_manager):
        engine = CustomerEngine(db_manager)
        customer_id = engine.create_customer("test@example.com", "Test User")
        customer = engine.get_customer(customer_id)
        assert customer is not None
        assert customer["email"] == "test@example.com"


# ============ ORDER TESTS ============

class TestOrderEngine:
    def test_create_order(self, db_manager, mock_event_bus):
        engine = OrderEngine(db_manager, mock_event_bus)
        order_id = engine.create_order("cust-123", [{"product_id": "prod-123", "quantity": 1}], 29.99)
        assert order_id is not None
        assert order_id.startswith("order-")
    
    def test_update_status(self, db_manager, mock_event_bus):
        engine = OrderEngine(db_manager, mock_event_bus)
        order_id = engine.create_order("cust-123", [{"product_id": "prod-123", "quantity": 1}], 29.99)
        success = engine.update_status(order_id, "pending_payment")
        assert success is True


# ============ LICENSE TESTS ============

class TestLicenseEngine:
    def test_issue_license(self, db_manager):
        engine = LicenseEngine(db_manager)
        license_id = engine.issue_license("cust-123", "prod-123", "order-123", "commercial")
        assert license_id is not None
    
    def test_activate_license(self, db_manager):
        engine = LicenseEngine(db_manager)
        license_id = engine.issue_license("cust-123", "prod-123", "order-123", "commercial")
        success = engine.activate_license(license_id, {"ip": "127.0.0.1"})
        assert success is True
    
    def test_validate_license(self, db_manager):
        engine = LicenseEngine(db_manager)
        license_id = engine.issue_license("cust-123", "prod-123", "order-123", "commercial")
        license_data = engine.get_license(license_id)
        assert license_data is not None


# ============ DELIVERY TESTS ============

class TestDigitalDeliveryEngine:
    def test_create_delivery(self, db_manager, temp_dir):
        engine = DigitalDeliveryEngine(db_manager, temp_dir)
        delivery_id = engine.create_delivery("order-123", "prod-123", "/path/to/file.zip")
        assert delivery_id is not None
    
    def test_get_download_url(self, db_manager, temp_dir):
        engine = DigitalDeliveryEngine(db_manager, temp_dir)
        delivery_id = engine.create_delivery("order-123", "prod-123", "/path/to/file.zip")
        url = engine.get_download_url(delivery_id)
        assert url is not None
        assert "/downloads/" in url


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
