#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Comprehensive Test Suite
Unit tests, integration tests, and test configuration.
"""

import os
import sys
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestConfig:
    """Test configuration"""
    
    @staticmethod
    def get_test_db_path() -> str:
        """Get temporary database path for tests"""
        temp_dir = tempfile.mkdtemp()
        return str(Path(temp_dir) / "test.db")
    
    @staticmethod
    def get_test_config() -> Dict[str, Any]:
        """Get test configuration"""
        return {
            "engine": {
                "name": "test-engine",
                "version": "1.0.0",
                "environment": "test"
            },
            "database": {
                "path": TestConfig.get_test_db_path(),
                "pool_size": 5,
                "timeout": 5
            },
            "logging": {
                "level": "DEBUG",
                "format": "text",
                "file_path": "logs/test.log"
            },
            "security": {
                "require_auth": False,
                "rate_limit": 1000,
                "rate_window": 60
            }
        }


# ============ SECURITY TESTS ============

class TestSecurityUtils:
    """Test security utilities"""
    
    def test_validate_email(self):
        from shared.security import validate_email
        assert validate_email("test@example.com") is True
        assert validate_email("invalid") is False
    
    def test_validate_uuid(self):
        from shared.security import validate_uuid
        assert validate_uuid("12345678-1234-1234-1234-123456789012") is True
        assert validate_uuid("invalid") is False
    
    def test_hash_password(self):
        from shared.security import SecurityUtils
        password_hash, salt = SecurityUtils.hash_password("test123")
        assert SecurityUtils.verify_password("test123", salt, password_hash) is True
        assert SecurityUtils.verify_password("wrong", salt, password_hash) is False
    
    def test_generate_api_key(self):
        from shared.security import SecurityUtils
        key1 = SecurityUtils.generate_api_key()
        key2 = SecurityUtils.generate_api_key()
        assert len(key1) > 0
        assert key1 != key2
    
    def test_rate_limiter(self):
        from shared.security import RateLimiter
        limiter = RateLimiter()
        assert limiter.is_allowed("test", 3, 60) is True
        assert limiter.is_allowed("test", 3, 60) is True


class TestAuth:
    """Test authentication system"""
    
    def test_create_user(self):
        from shared.auth import AuthManager
        from shared.database import DatabaseManager
        
        db_path = TestConfig.get_test_db_path()
        db = DatabaseManager(db_path)
        
        # Create users table
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
        api_key = auth.create_user("test@example.com", "operator", ["read"])
        
        assert api_key is not None
        assert len(api_key) > 0
        
        db.close()
    
    def test_authenticate(self):
        from shared.auth import AuthManager
        from shared.database import DatabaseManager
        
        db_path = TestConfig.get_test_db_path()
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
        api_key = auth.create_user("test@example.com", "operator", ["read"])
        
        context = auth.authenticate(api_key)
        assert context is not None
        assert context.is_authenticated is True
        assert context.user.email == "test@example.com"
        
        # Test invalid key
        context = auth.authenticate("invalid-key")
        assert context is None
        
        db.close()


# ============ VALIDATION TESTS ============

class TestValidation:
    """Test validation system"""
    
    def test_validate_email(self):
        from shared.validation import FieldValidator
        assert FieldValidator.email("test@example.com", "email") == "test@example.com"
        with pytest.raises(Exception):
            FieldValidator.email("invalid", "email")
    
    def test_validate_string(self):
        from shared.validation import FieldValidator
        assert FieldValidator.string("hello", "name") == "hello"
        with pytest.raises(Exception):
            FieldValidator.string("", "name", min_length=1)
    
    def test_validate_integer(self):
        from shared.validation import FieldValidator
        assert FieldValidator.integer(42, "age") == 42
        with pytest.raises(Exception):
            FieldValidator.integer(-1, "age", min_value=0)
    
    def test_request_validator(self):
        from shared.validation import RequestValidator
        validator = RequestValidator()
        
        schema = {
            "email": {"type": "email", "required": True},
            "name": {"type": "string", "required": True}
        }
        
        data = {"email": "test@example.com", "name": "John"}
        result = validator.validate(data, schema)
        assert result["email"] == "test@example.com"
        assert result["name"] == "John"


# ============ DATABASE TESTS ============

class TestDatabase:
    """Test database system"""
    
    def test_connection_pool(self):
        from shared.database import DatabaseManager
        db_path = TestConfig.get_test_db_path()
        db = DatabaseManager(db_path)
        
        with db.get_connection() as conn:
            result = conn.execute("SELECT 1").fetchone()
            assert result[0] == 1
        
        db.close()
    
    def test_query_builder(self):
        from shared.database import QueryBuilder
        builder = QueryBuilder("users")
        builder.where("id = ?", "123").where("active = ?", 1)
        query, params = builder.build_select()
        
        assert "SELECT" in query
        assert "WHERE" in query
        assert len(params) == 2
    
    def test_transaction(self):
        from shared.database import DatabaseManager
        db_path = TestConfig.get_test_db_path()
        db = DatabaseManager(db_path)
        
        db.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT)")
        
        queries = [
            ("INSERT INTO test (name) VALUES (?)", ("Alice",)),
            ("INSERT INTO test (name) VALUES (?)", ("Bob",))
        ]
        db.transaction(queries)
        
        results = db.execute("SELECT * FROM test")
        assert len(results) == 2
        
        db.close()


# ============ UTILITY TESTS ============

class TestUtils:
    """Test utility functions"""
    
    def test_id_generator(self):
        from shared.utils import IDGenerator
        id1 = IDGenerator.generate_id("test-")
        assert id1.startswith("test-")
        assert len(id1) > 10
    
    def test_time_utils(self):
        from shared.utils import TimeUtils
        now = TimeUtils.now_iso()
        assert isinstance(now, str)
        assert "T" in now
    
    def test_hash_utils(self):
        from shared.utils import HashUtils
        hash_value = HashUtils.sha256("test")
        assert len(hash_value) == 64


# ============ CACHE TESTS ============

class TestCache:
    """Test cache system"""
    
    def test_memory_cache(self):
        from shared.cache import InMemoryCache
        cache = InMemoryCache(max_size=100)
        
        cache.set("key1", {"value": "test"}, ttl=60)
        result = cache.get("key1")
        assert result == {"value": "test"}
        
        cache.delete("key1")
        assert cache.get("key1") is None
    
    def test_cache_manager(self):
        from shared.cache import CacheManager
        cache = CacheManager()
        
        cache.set("test-key", {"data": "test"}, ttl=60)
        result = cache.get("test-key")
        assert result == {"data": "test"}


# ============ HEALTH TESTS ============

class TestHealth:
    """Test health system"""
    
    def test_health_monitor(self):
        from shared.health import HealthMonitor, DiskHealthChecker
        monitor = HealthMonitor()
        monitor.register_checker(DiskHealthChecker("/", min_free_gb=0.1))
        
        # Just test initialization
        assert len(monitor._checkers) > 0


# ============ CONFIGURATION ============

def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow tests")


@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration"""
    return TestConfig()


@pytest.fixture(scope="function")
def temp_dir():
    """Create temporary directory for each test"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture(scope="function")
def db_manager(temp_dir):
    """Create database manager for each test"""
    from shared.database import DatabaseManager
    db_path = temp_dir / "test.db"
    return DatabaseManager(db_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
