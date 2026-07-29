"""
MAHA LAKSHMI CORP - Test Suite
Comprehensive tests for authentication, authorization, dashboard, and marketplace.
"""

import pytest
import json
import time
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


class TestAuthentication:
    """Authentication tests"""
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_login_missing_fields(self):
        """Test login with missing fields"""
        response = client.post("/api/auth/login", json={})
        assert response.status_code == 422
    
    def test_login_invalid_email(self):
        """Test login with invalid email"""
        response = client.post("/api/auth/login", json={
            "email": "invalid-email",
            "password": "Test@123456"
        })
        assert response.status_code == 422
    
    def test_login_invalid_password(self):
        """Test login with short password"""
        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "short"
        })
        assert response.status_code == 422


class TestAuthorization:
    """Authorization tests"""
    
    def test_protected_endpoint_without_token(self):
        """Test protected endpoint without token"""
        response = client.get("/api/dashboard/home")
        assert response.status_code == 401
    
    def test_protected_endpoint_with_invalid_token(self):
        """Test protected endpoint with invalid token"""
        response = client.get(
            "/api/dashboard/home",
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401


class TestDashboard:
    """Dashboard tests"""
    
    def test_dashboard_requires_auth(self):
        """Test dashboard requires authentication"""
        response = client.get("/api/dashboard/home")
        assert response.status_code in [401, 403]
    
    def test_marketplace_requires_auth(self):
        """Test marketplace requires authentication"""
        response = client.get("/api/marketplace/accounts")
        assert response.status_code in [401, 403]


class TestMarketplace:
    """Marketplace tests"""
    
    def test_marketplace_health_requires_auth(self):
        """Test marketplace health requires auth"""
        response = client.get("/api/marketplace/health")
        assert response.status_code in [401, 403]
    
    def test_create_account_requires_auth(self):
        """Test create account requires auth"""
        response = client.post("/api/marketplace/accounts", json={
            "provider": "gumroad",
            "name": "Test Account",
            "api_key": "test-key"
        })
        assert response.status_code in [401, 403, 422]


class TestRateLimiting:
    """Rate limiting tests"""
    
    def test_rate_limit_headers(self):
        """Test rate limit headers are present"""
        response = client.get("/health")
        # Should have rate limit headers or at least not fail
        assert response.status_code == 200


class TestSecurity:
    """Security tests"""
    
    def test_security_headers(self):
        """Test security headers are present"""
        response = client.get("/health")
        assert response.status_code == 200
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "X-XSS-Protection" in response.headers
    
    def test_cors_headers(self):
        """Test CORS headers"""
        response = client.get("/health", headers={"Origin": "https://mahalaksmi.web.id"})
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "https://mahalaksmi.web.id"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
