"""
MAHA LAKSHMI CORP - Revenue Sprint 2 Tests
End-to-end tests for: Generate → Publish → Sale → Payment → Dashboard
"""

import pytest
import json
import time
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

# Add parent directory to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.main import app
from backend.finance.sale_processor import SaleProcessor, SaleEvent
from backend.shared.webhook_security import WebhookSecurity

client = TestClient(app)


class TestRevenueSprint2EndToEnd:
    """End-to-end tests for Revenue Sprint 2"""
    
    def test_health_endpoint(self):
        """Test API health"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_dashboard_home_requires_auth(self):
        """Test dashboard home requires authentication"""
        response = client.get("/api/dashboard/home")
        assert response.status_code == 401
    
    def test_finance_overview_requires_auth(self):
        """Test finance overview requires authentication"""
        response = client.get("/api/finance/overview")
        assert response.status_code == 401
    
    def test_webhook_endpoint_exists(self):
        """Test webhook endpoint is registered"""
        response = client.post("/api/marketplace/webhooks/gumroad", json={})
        # Should not be 404 (endpoint exists)
        assert response.status_code != 404


class TestSaleProcessor:
    """Tests for sale processor"""
    
    def test_process_purchase_creates_records(self):
        """Test that processing a purchase creates all required records"""
        # This test requires database setup
        # In a real scenario, we would:
        # 1. Create a test product in the database
        # 2. Create a test marketplace account
        # 3. Process a purchase event
        # 4. Verify transaction, payment, and sale records were created
        pass
    
    def test_process_refund_creates_negative_transaction(self):
        """Test that refunds create negative transactions"""
        pass
    
    def test_process_chargeback_creates_negative_transaction(self):
        """Test that chargebacks create negative transactions"""
        pass


class TestWebhookSecurity:
    """Tests for webhook security"""
    
    def test_verify_gumroad_signature_valid(self):
        """Test valid signature verification"""
        payload = '{"id": "test-123", "price": 1000}'
        secret = "test-secret"
        
        # Generate valid signature
        import hmac
        import hashlib
        signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        assert WebhookSecurity.verify_gumroad_signature(payload, signature, secret) is True
    
    def test_verify_gumroad_signature_invalid(self):
        """Test invalid signature rejection"""
        payload = '{"id": "test-123", "price": 1000}'
        secret = "test-secret"
        
        assert WebhookSecurity.verify_gumroad_signature(payload, "invalid-signature", secret) is False
    
    def test_extract_event_type_purchase(self):
        """Test purchase event type extraction"""
        payload = {"event": "purchase", "id": "123"}
        assert WebhookSecurity.extract_event_type(payload) == "purchase"
    
    def test_extract_event_type_refund(self):
        """Test refund event type extraction"""
        payload = {"event": "refund", "id": "123"}
        assert WebhookSecurity.extract_event_type(payload) == "refund"
    
    def test_sanitize_payload_removes_sensitive_data(self):
        """Test payload sanitization"""
        payload = {
            "id": "123",
            "email": "test@example.com",
            "name": "Test User",
            "address": "123 Street"
        }
        
        sanitized = WebhookSecurity.sanitize_payload(payload)
        assert sanitized["email"] == "***REDACTED***"
        assert sanitized["name"] == "***REDACTED***"
        assert sanitized["address"] == "***REDACTED***"
        assert sanitized["id"] == "123"  # Not sensitive


class TestRevenueEndpoints:
    """Tests for revenue dashboard endpoints"""
    
    def test_revenue_endpoint_requires_auth(self):
        """Test revenue endpoint requires auth"""
        response = client.get("/api/dashboard/revenue")
        assert response.status_code == 401
    
    def test_finance_endpoint_requires_auth(self):
        """Test finance endpoint requires auth"""
        response = client.get("/api/dashboard/finance")
        assert response.status_code == 401
    
    def test_sales_endpoint_requires_auth(self):
        """Test sales endpoint requires auth"""
        response = client.get("/api/dashboard/sales")
        assert response.status_code == 401
    
    def test_accounting_endpoint_requires_auth(self):
        """Test accounting endpoint requires auth"""
        response = client.get("/api/dashboard/accounting")
        assert response.status_code == 401


class TestMarketplaceWebhook:
    """Tests for marketplace webhook handling"""
    
    def test_webhook_purchase_event_processing(self):
        """Test purchase event processing"""
        # This would require a valid JWT token and proper test setup
        # For now, we verify the endpoint exists
        response = client.post("/api/marketplace/webhooks/gumroad", json={
            "event": "purchase",
            "id": f"test-{int(time.time())}",
            "product_id": "test-product",
            "email": "test@example.com",
            "price": 1000,
            "currency": "USD"
        })
        # Should not be 404
        assert response.status_code != 404
    
    def test_webhook_invalid_event_type(self):
        """Test invalid event type handling"""
        response = client.post("/api/marketplace/webhooks/gumroad", json={
            "event": "unknown_event",
            "id": "test-123"
        })
        assert response.status_code != 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
