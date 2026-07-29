#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Integration Tests
End-to-end integration tests for all services.
"""

import os
import sys
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from unittest.mock import Mock, patch, AsyncMock

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestIntegration:
    """Integration tests"""
    
    def test_database_integration(self):
        """Test database operations"""
        from shared.database import DatabaseManager
        
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        try:
            db = DatabaseManager(db_path)
            
            # Create table
            db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
            
            # Insert data
            db.execute("INSERT INTO users (name) VALUES (?)", ("Alice",))
            db.execute("INSERT INTO users (name) VALUES (?)", ("Bob",))
            
            # Query data
            results = db.execute("SELECT * FROM users")
            assert len(results) == 2
            
            db.close()
        finally:
            Path(db_path).unlink(missing_ok=True)
    
    def test_auth_integration(self):
        """Test authentication flow"""
        from shared.auth import AuthManager
        from shared.database import DatabaseManager
        from shared.security import validate_email
        
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        try:
            db = DatabaseManager(db_path)
            
            db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    role TEXT NOT NULL,
                    permissions TEXT NOT NULL,
                    api_key TEXT UNIQUE NOT NULL,
                    is_active INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            
            auth = AuthManager(db)
            
            # Create user
            api_key = auth.create_user("test@example.com", "admin", ["read", "write", "admin"])
            assert api_key is not None
            
            # Authenticate
            context = auth.authenticate(api_key)
            assert context is not None
            assert context.is_authenticated is True
            assert context.user.role == "admin"
            assert "admin" in context.permissions
            
            # Authorize
            assert auth.authorize(context, "read") is True
            assert auth.authorize(context, "write") is True
            assert auth.authorize(context, "delete") is False
            
            db.close()
        finally:
            Path(db_path).unlink(missing_ok=True)
    
    def test_cache_integration(self):
        """Test cache operations"""
        from shared.cache import CacheManager
        
        cache = CacheManager()
        
        # Test set/get
        test_data = {"user_id": "123", "name": "Alice"}
        cache.set("user:123", test_data, ttl=60)
        result = cache.get("user:123")
        assert result == test_data
        
        # Test delete
        cache.delete("user:123")
        assert cache.get("user:123") is None
    
    def test_validation_integration(self):
        """Test validation flow"""
        from shared.validation import RequestValidator
        
        validator = RequestValidator()
        
        schema = {
            "email": {"type": "email", "required": True},
            "age": {"type": "integer", "min_value": 0, "max_value": 150}
        }
        
        # Valid data
        valid_data = {"email": "test@example.com", "age": 25}
        result = validator.validate(valid_data, schema)
        assert result["email"] == "test@example.com"
        assert result["age"] == 25
        
        # Invalid data
        invalid_data = {"email": "invalid", "age": -5}
        with pytest.raises(Exception):
            validator.validate(invalid_data, schema)


class TestProductFactory:
    """Test product factory"""
    
    def test_product_generation(self):
        """Test product generation"""
        # Mock the product factory
        from product_factory.generator import ProductGenerator
        generator = ProductGenerator()
        
        # Test would require actual implementation
        assert generator is not None


class TestMarketplace:
    """Test marketplace"""
    
    def test_listing_creation(self):
        """Test marketplace listing creation"""
        # Mock the marketplace
        from marketplace.marketplace_manager import MarketplaceManager
        manager = MarketplaceManager()
        
        # Test would require actual implementation
        assert manager is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
