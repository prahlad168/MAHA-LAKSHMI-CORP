#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Shared Test Suite
Comprehensive tests for shared modules with high coverage.
"""

import os
import sys
import json
import time
import tempfile
import shutil
import pytest
from pathlib import Path
from typing import Dict, Any, Optional
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))


# ============ FIXTURES ============

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


@pytest.fixture
def sample_schema():
    """Sample validation schema"""
    return {
        "email": {"type": "email", "required": True},
        "name": {"type": "string", "required": True, "max_length": 100, "min_length": 2},
        "age": {"type": "integer", "min_value": 0, "max_value": 150},
        "price": {"type": "float", "min_value": 0.0},
        "status": {"type": "enum", "values": ["active", "inactive", "pending"]},
        "tags": {"type": "list", "max_items": 10},
        "metadata": {"type": "dict"}
    }


# ============ SECURITY TESTS ============

class TestSecurityUtils:
    """Test security utilities"""
    
    def test_validate_email_valid(self):
        from shared.security import validate_email
        assert validate_email("test@example.com") is True
        assert validate_email("user.name+tag@domain.co.id") is True
    
    def test_validate_email_invalid(self):
        from shared.security import validate_email
        assert validate_email("invalid") is False
        assert validate_email("missing@domain") is False
        assert validate_email("@domain.com") is False
    
    def test_validate_uuid_valid(self):
        from shared.security import validate_uuid
        assert validate_uuid("12345678-1234-1234-1234-123456789012") is True
        assert validate_uuid("ABCDEF12-3456-7890-ABCD-EF1234567890") is True
    
    def test_validate_uuid_invalid(self):
        from shared.security import validate_uuid
        assert validate_uuid("invalid") is False
        assert validate_uuid("12345678-1234-1234-1234-12345678901") is False
    
    def test_hash_password(self):
        from shared.security import SecurityUtils
        password_hash, salt = SecurityUtils.hash_password("test123")
        assert SecurityUtils.verify_password("test123", salt, password_hash) is True
        assert SecurityUtils.verify_password("wrong", salt, password_hash) is False
        assert len(password_hash) > 0
        assert len(salt) > 0
    
    def test_generate_api_key(self):
        from shared.security import SecurityUtils
        key1 = SecurityUtils.generate_api_key()
        key2 = SecurityUtils.generate_api_key()
        assert len(key1) > 0
        assert key1 != key2
        assert isinstance(key1, str)
    
    def test_generate_secret(self):
        from shared.security import SecurityUtils
        secret1 = SecurityUtils.generate_secret()
        secret2 = SecurityUtils.generate_secret()
        assert len(secret1) > 0
        assert secret1 != secret2
    
    def test_rate_limiter_allow(self):
        from shared.security import RateLimiter
        limiter = RateLimiter()
        assert limiter.is_allowed("test", 3, 60) is True
        assert limiter.is_allowed("test", 3, 60) is True
        assert limiter.is_allowed("test", 3, 60) is True
    
    def test_rate_limiter_deny(self):
        from shared.security import RateLimiter
        limiter = RateLimiter()
        for _ in range(3):
            limiter.is_allowed("test", 3, 60)
        assert limiter.is_allowed("test", 3, 60) is False
    
    def test_rate_limiter_different_keys(self):
        from shared.security import RateLimiter
        limiter = RateLimiter()
        assert limiter.is_allowed("key1", 1, 60) is True
        assert limiter.is_allowed("key2", 1, 60) is True
        assert limiter.is_allowed("key1", 1, 60) is False  # key1 exhausted
    
    def test_webhook_signature(self):
        from shared.security import SecurityUtils
        payload = b"test payload"
        secret = "test-secret"
        signature = SecurityUtils.verify_webhook_signature(payload, "wrong", secret)
        assert signature is False
    
    def test_security_headers(self):
        from shared.security import get_security_headers
        headers = get_security_headers()
        assert "X-Content-Type-Options" in headers
        assert "X-Frame-Options" in headers
        assert "Strict-Transport-Security" in headers


# ============ AUTH TESTS ============

class TestAuth:
    """Test authentication system"""
    
    def test_create_user(self, db_manager):
        from shared.auth import AuthManager
        from shared.security import validate_email
        
        db_manager.execute("""
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
        
        auth = AuthManager(db_manager)
        api_key = auth.create_user("test@example.com", "operator", ["read"])
        
        assert api_key is not None
        assert isinstance(api_key, str)
        assert len(api_key) > 0
    
    def test_create_user_invalid_email(self, db_manager):
        from shared.auth import AuthManager
        
        db_manager.execute("""
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
        
        auth = AuthManager(db_manager)
        api_key = auth.create_user("invalid-email", "operator", ["read"])
        assert api_key is None
    
    def test_authenticate_valid(self, db_manager):
        from shared.auth import AuthManager
        
        db_manager.execute("""
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
        
        auth = AuthManager(db_manager)
        api_key = auth.create_user("test@example.com", "admin", ["read", "write", "admin"])
        
        context = auth.authenticate(api_key)
        assert context is not None
        assert context.is_authenticated is True
        assert context.user.email == "test@example.com"
        assert context.user.role == "admin"
        assert "admin" in context.permissions
    
    def test_authenticate_invalid(self, db_manager):
        from shared.auth import AuthManager
        
        db_manager.execute("""
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
        
        auth = AuthManager(db_manager)
        context = auth.authenticate("invalid-key")
        assert context is None
    
    def test_authorize_admin(self, db_manager):
        from shared.auth import AuthManager
        
        db_manager.execute("""
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
        
        auth = AuthManager(db_manager)
        api_key = auth.create_user("test@example.com", "admin", ["read", "write", "admin"])
        context = auth.authenticate(api_key)
        
        assert auth.authorize(context, "read") is True
        assert auth.authorize(context, "write") is True
        assert auth.authorize(context, "delete") is True  # admin has all
    
    def test_authorize_operator(self, db_manager):
        from shared.auth import AuthManager
        
        db_manager.execute("""
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
        
        auth = AuthManager(db_manager)
        api_key = auth.create_user("test@example.com", "operator", ["read"])
        context = auth.authenticate(api_key)
        
        assert auth.authorize(context, "read") is True
        assert auth.authorize(context, "write") is False
        assert auth.authorize(context, "delete") is False


# ============ VALIDATION TESTS ============

class TestFieldValidator:
    """Test field validators"""
    
    def test_required_valid(self):
        from shared.validation import FieldValidator
        assert FieldValidator.required("value", "field") == "value"
    
    def test_required_invalid(self):
        from shared.validation import FieldValidator
        with pytest.raises(Exception):
            FieldValidator.required(None, "field")
        with pytest.raises(Exception):
            FieldValidator.required("", "field")
    
    def test_string_valid(self):
        from shared.validation import FieldValidator
        assert FieldValidator.string("hello", "name") == "hello"
        assert FieldValidator.string("  test  ", "name") == "test"
    
    def test_string_too_short(self):
        from shared.validation import FieldValidator
        with pytest.raises(Exception):
            FieldValidator.string("ab", "name", min_length=3)
    
    def test_string_too_long(self):
        from shared.validation import FieldValidator
        with pytest.raises(Exception):
            FieldValidator.string("a" * 101, "name", max_length=100)
    
    def test_integer_valid(self):
        from shared.validation import FieldValidator
        assert FieldValidator.integer(42, "age") == 42
        assert FieldValidator.integer(0, "age", min_value=0) == 0
    
    def test_integer_out_of_range(self):
        from shared.validation import FieldValidator
        with pytest.raises(Exception):
            FieldValidator.integer(-1, "age", min_value=0)
        with pytest.raises(Exception):
            FieldValidator.integer(200, "age", max_value=150)
    
    def test_float_valid(self):
        from shared.validation import FieldValidator
        assert FieldValidator.float(19.99, "price") == 19.99
        assert FieldValidator.float(10, "price") == 10.0
    
    def test_email_valid(self):
        from shared.validation import FieldValidator
        assert FieldValidator.email("test@example.com", "email") == "test@example.com"
        assert FieldValidator.email("USER@DOMAIN.COM", "email") == "user@domain.com"
    
    def test_email_invalid(self):
        from shared.validation import FieldValidator
        with pytest.raises(Exception):
            FieldValidator.email("invalid", "email")
    
    def test_uuid_valid(self):
        from shared.validation import FieldValidator
        assert FieldValidator.uuid("12345678-1234-1234-1234-123456789012", "id") == "12345678-1234-1234-1234-123456789012"
    
    def test_uuid_invalid(self):
        from shared.validation import FieldValidator
        with pytest.raises(Exception):
            FieldValidator.uuid("invalid", "id")
    
    def test_enum_valid(self):
        from shared.validation import FieldValidator
        assert FieldValidator.enum_value("active", "status", ["active", "inactive"]) == "active"
    
    def test_enum_invalid(self):
        from shared.validation import FieldValidator
        with pytest.raises(Exception):
            FieldValidator.enum_value("invalid", "status", ["active", "inactive"])
    
    def test_list_valid(self):
        from shared.validation import FieldValidator
        assert FieldValidator.list([1, 2, 3], "tags") == [1, 2, 3]
    
    def test_list_invalid(self):
        from shared.validation import FieldValidator
        with pytest.raises(Exception):
            FieldValidator.list("not a list", "tags")
    
    def test_dict_valid(self):
        from shared.validation import FieldValidator
        assert FieldValidator.dict({"key": "value"}, "metadata") == {"key": "value"}
    
    def test_dict_invalid(self):
        from shared.validation import FieldValidator
        with pytest.raises(Exception):
            FieldValidator.dict("not a dict", "metadata")


class TestRequestValidator:
    """Test request validator"""
    
    def test_validate_valid_data(self, sample_schema):
        from shared.validation import RequestValidator
        validator = RequestValidator()
        
        data = {
            "email": "test@example.com",
            "name": "John Doe",
            "age": 30,
            "price": 19.99,
            "status": "active",
            "tags": ["tag1", "tag2"],
            "metadata": {"key": "value"}
        }
        
        result = validator.validate(data, sample_schema)
        assert result["email"] == "test@example.com"
        assert result["name"] == "John Doe"
        assert result["age"] == 30
    
    def test_validate_missing_required(self, sample_schema):
        from shared.validation import RequestValidator
        validator = RequestValidator()
        
        data = {"age": 30}  # missing email and name
        with pytest.raises(Exception):
            validator.validate(data, sample_schema)
    
    def test_validate_invalid_email(self, sample_schema):
        from shared.validation import RequestValidator
        validator = RequestValidator()
        
        data = {"email": "invalid", "name": "John"}
        with pytest.raises(Exception):
            validator.validate(data, sample_schema)
    
    def test_validate_age_out_of_range(self, sample_schema):
        from shared.validation import RequestValidator
        validator = RequestValidator()
        
        data = {"email": "test@example.com", "name": "John", "age": -1}
        with pytest.raises(Exception):
            validator.validate(data, sample_schema)


# ============ DATABASE TESTS ============

class TestDatabase:
    """Test database system"""
    
    def test_connection_pool(self, temp_dir):
        from shared.database import DatabaseManager
        db_path = temp_dir / "test.db"
        db = DatabaseManager(db_path)
        
        with db.get_connection() as conn:
            result = conn.execute("SELECT 1").fetchone()
            assert result[0] == 1
        
        db.close()
    
    def test_execute_query(self, db_manager):
        db_manager.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
        db_manager.execute("INSERT INTO users (name) VALUES (?)", ("Alice",))
        
        results = db_manager.execute("SELECT * FROM users")
        assert len(results) == 1
        assert results[0]["name"] == "Alice"
    
    def test_execute_one(self, db_manager):
        db_manager.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
        db_manager.execute("INSERT INTO users (name) VALUES (?)", ("Alice",))
        
        result = db_manager.execute_one("SELECT * FROM users WHERE name = ?", ("Alice",))
        assert result is not None
        assert result["name"] == "Alice"
    
    def test_execute_one_not_found(self, db_manager):
        db_manager.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
        result = db_manager.execute_one("SELECT * FROM users WHERE name = ?", ("Nonexistent",))
        assert result is None
    
    def test_execute_many(self, db_manager):
        db_manager.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
        
        queries = [
            ("INSERT INTO users (name) VALUES (?)", ("Alice",)),
            ("INSERT INTO users (name) VALUES (?)", ("Bob",)),
            ("INSERT INTO users (name) VALUES (?)", ("Charlie",))
        ]
        db_manager.execute_many("INSERT INTO users (name) VALUES (?)", [("Alice",), ("Bob",), ("Charlie",)])
        
        results = db_manager.execute("SELECT * FROM users")
        assert len(results) == 3
    
    def test_transaction(self, db_manager):
        db_manager.execute("CREATE TABLE IF NOT EXISTS accounts (id INTEGER PRIMARY KEY, balance REAL)")
        db_manager.execute("INSERT INTO accounts (balance) VALUES (?)", (1000.0,))
        
        queries = [
            ("UPDATE accounts SET balance = balance - ? WHERE id = ?", (100.0, 1)),
            ("UPDATE accounts SET balance = balance + ? WHERE id = ?", (100.0, 1))
        ]
        db_manager.transaction(queries)
        
        result = db_manager.execute_one("SELECT balance FROM accounts WHERE id = ?", (1,))
        assert result["balance"] == 1000.0
    
    def test_query_builder_select(self):
        from shared.database import QueryBuilder
        builder = QueryBuilder("users")
        builder.where("id = ?", "123").where("active = ?", 1)
        query, params = builder.build_select()
        
        assert "SELECT" in query
        assert "FROM users" in query
        assert "WHERE" in query
        assert "id = ?" in query
        assert "active = ?" in query
        assert params == ["123", 1]
    
    def test_query_builder_order_by(self):
        from shared.database import QueryBuilder
        builder = QueryBuilder("users")
        builder.order_by("created_at", desc=True)
        query, params = builder.build_select()
        
        assert "ORDER BY created_at DESC" in query
    
    def test_query_builder_limit(self):
        from shared.database import QueryBuilder
        builder = QueryBuilder("users")
        builder.limit(10, 20)
        query, params = builder.build_select()
        
        assert "LIMIT 10 OFFSET 20" in query
    
    def test_query_builder_delete(self):
        from shared.database import QueryBuilder
        builder = QueryBuilder("users")
        builder.where("id = ?", "123")
        query, params = builder.build_delete()
        
        assert "DELETE FROM users" in query
        assert "WHERE" in query
        assert params == ["123"]


# ============ UTILITY TESTS ============

class TestUtils:
    """Test utility functions"""
    
    def test_generate_id(self):
        from shared.utils import IDGenerator
        id1 = IDGenerator.generate_id("test-")
        assert id1.startswith("test-")
        assert len(id1) > 10
    
    def test_generate_uuid(self):
        from shared.utils import IDGenerator
        uuid1 = IDGenerator.generate_uuid()
        uuid2 = IDGenerator.generate_uuid()
        assert uuid1 != uuid2
        assert len(uuid1) == 36
    
    def test_generate_short_id(self):
        from shared.utils import IDGenerator
        short_id = IDGenerator.generate_short_id()
        assert len(short_id) == 12
        assert isinstance(short_id, str)
    
    def test_now_iso(self):
        from shared.utils import TimeUtils
        now = TimeUtils.now_iso()
        assert isinstance(now, str)
        assert "T" in now
    
    def test_now_timestamp(self):
        from shared.utils import TimeUtils
        ts = TimeUtils.now_timestamp()
        assert isinstance(ts, int)
        assert ts > 0
    
    def test_is_expired(self):
        from shared.utils import TimeUtils
        past = (datetime.now() - timedelta(hours=1)).isoformat()
        future = (datetime.now() + timedelta(hours=1)).isoformat()
        assert TimeUtils.is_expired(past) is True
        assert TimeUtils.is_expired(future) is False
    
    def test_sha256(self):
        from shared.utils import HashUtils
        hash_value = HashUtils.sha256("test")
        assert len(hash_value) == 64
        assert HashUtils.sha256("test") == HashUtils.sha256("test")
    
    def test_md5(self):
        from shared.utils import HashUtils
        hash_value = HashUtils.md5("test")
        assert len(hash_value) == 32
    
    def test_retry_success(self):
        from shared.utils import retry
        
        call_count = 0
        @retry(max_attempts=3)
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Temporary error")
            return "success"
        
        result = flaky_function()
        assert result == "success"
        assert call_count == 2
    
    def test_retry_failure(self):
        from shared.utils import retry
        
        @retry(max_attempts=2)
        def always_fails():
            raise ValueError("Permanent error")
        
        with pytest.raises(ValueError):
            always_fails()


# ============ CACHE TESTS ============

class TestInMemoryCache:
    """Test in-memory cache"""
    
    def test_set_get(self):
        from shared.cache import InMemoryCache
        cache = InMemoryCache(max_size=100)
        cache.set("key1", {"value": "test"}, ttl=60)
        result = cache.get("key1")
        assert result == {"value": "test"}
    
    def test_get_missing(self):
        from shared.cache import InMemoryCache
        cache = InMemoryCache()
        assert cache.get("nonexistent") is None
    
    def test_delete(self):
        from shared.cache import InMemoryCache
        cache = InMemoryCache()
        cache.set("key1", "value1")
        cache.delete("key1")
        assert cache.get("key1") is None
    
    def test_clear(self):
        from shared.cache import InMemoryCache
        cache = InMemoryCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None
    
    def test_ttl_expiry(self):
        from shared.cache import InMemoryCache
        import time
        cache = InMemoryCache()
        cache.set("key1", "value1", ttl=1)
        time.sleep(1.1)
        assert cache.get("key1") is None
    
    def test_lru_eviction(self):
        from shared.cache import InMemoryCache
        cache = InMemoryCache(max_size=2)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # Should evict oldest
        assert cache.get("key1") is None
        assert cache.get("key2") is not None
    
    def test_stats(self):
        from shared.cache import InMemoryCache
        cache = InMemoryCache()
        cache.set("key1", "value1")
        cache.get("key1")  # hit
        cache.get("missing")  # miss
        
        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["size"] == 1


class TestCacheManager:
    """Test cache manager"""
    
    def test_set_get(self):
        from shared.cache import CacheManager
        cache = CacheManager()
        cache.set("test-key", {"data": "test"}, ttl=60)
        result = cache.get("test-key")
        assert result == {"data": "test"}
    
    def test_delete(self):
        from shared.cache import CacheManager
        cache = CacheManager()
        cache.set("test-key", "value")
        cache.delete("test-key")
        assert cache.get("test-key") is None
    
    def test_get_or_set(self):
        from shared.cache import CacheManager
        cache = CacheManager()
        
        factory_called = False
        def factory():
            nonlocal factory_called
            factory_called = True
            return {"fresh": True}
        
        result = cache.get_or_set("or-set-key", factory, ttl=60)
        assert result == {"fresh": True}
        assert factory_called is True
        
        # Second call should use cache
        result2 = cache.get_or_set("or-set-key", factory, ttl=60)
        assert result2 == {"fresh": True}
        assert factory_called is True  # Factory should not be called again


# ============ HEALTH TESTS ============

class TestHealthChecker:
    """Test health checker"""
    
    def test_disk_health(self):
        from shared.health import DiskHealthChecker, HealthMonitor
        monitor = HealthMonitor()
        checker = DiskHealthChecker("/", min_free_gb=0.01)
        
        # Just verify it initializes and can be called
        assert checker.name == "disk"
        assert checker.critical is True


class TestHealthMonitor:
    """Test health monitor"""
    
    def test_register_checker(self):
        from shared.health import HealthMonitor, DiskHealthChecker
        monitor = HealthMonitor()
        checker = DiskHealthChecker("/", min_free_gb=0.01)
        monitor.register_checker(checker)
        assert len(monitor._checkers) == 1
    
    def test_get_simple_health(self):
        from shared.health import HealthMonitor
        monitor = HealthMonitor()
        result = monitor.get_simple_health()
        assert "status" in result


# ============ METRICS TESTS ============

class TestMetrics:
    """Test metrics system"""
    
    def test_increment_counter(self):
        from shared.monitoring import MetricsCollector
        metrics = MetricsCollector()
        metrics.increment("requests", 1.0, {"endpoint": "/test"})
        assert metrics.get_counter("requests", {"endpoint": "/test"}) == 1.0
    
    def test_gauge(self):
        from shared.monitoring import MetricsCollector
        metrics = MetricsCollector()
        metrics.gauge("memory_usage", 75.5, {"type": "heap"})
        assert metrics.get_gauge("memory_usage", {"type": "heap"}) == 75.5
    
    def test_histogram(self):
        from shared.monitoring import MetricsCollector
        metrics = MetricsCollector()
        metrics.histogram("latency", 0.123)
        metrics.histogram("latency", 0.456)
        metrics.histogram("latency", 0.789)
        
        stats = metrics.get_histogram_stats("latency")
        assert stats["count"] == 3
        assert stats["min"] == 0.123
        assert stats["max"] == 0.789
        assert stats["avg"] == pytest.approx(0.456, 0.01)


# ============ CORE ENGINE TESTS ============

class TestCoreEngine:
    """Test core engine"""
    
    def test_engine_singleton(self):
        from shared.core_engine import CoreEngine, get_engine
        engine1 = CoreEngine()
        engine2 = CoreEngine()
        assert engine1 is engine2
    
    def test_engine_register_module(self):
        from shared.core_engine import CoreEngine
        engine = CoreEngine()
        engine.register_module("test", Mock())
        assert engine.get_module("test") is not None
    
    def test_engine_get_health(self):
        from shared.core_engine import CoreEngine
        engine = CoreEngine()
        health = engine.get_health()
        assert "status" in health
        assert "modules" in health


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=shared", "--cov-report=term-missing"])
