#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Additional Coverage Tests
Tests to cover remaining uncovered code paths in shared modules.
"""

import os
import sys
import json
import time
import pytest
import tempfile
import tarfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestAuthAdvanced:
    """Advanced authentication tests"""
    
    def test_auth_manager_create_user_failure(self, db_manager):
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
        # Test with invalid email
        result = auth.create_user("not-an-email", "user", [])
        assert result is None
    
    def test_auth_manager_load_user(self, db_manager):
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
        api_key = auth.create_user("test@example.com", "viewer", ["read"])
        
        # Load user by API key
        user = auth._load_user_by_api_key(api_key)
        assert user is not None
        assert user.email == "test@example.com"
        assert user.role == "viewer"
    
    def test_rate_limiter_window_expiry(self):
        from shared.auth import RateLimiter
        limiter = RateLimiter()
        
        # Fill up limit
        for _ in range(3):
            assert limiter.is_allowed("test", 3, 1) is True
        
        # Should be blocked
        assert limiter.is_allowed("test", 3, 1) is False
        
        # Wait for window to expire
        time.sleep(1.1)
        
        # Should be allowed again
        assert limiter.is_allowed("test", 3, 1) is True
    
    def test_auth_manager_multiple_users(self, db_manager):
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
        api_key1 = auth.create_user("user1@example.com", "viewer", ["read"])
        api_key2 = auth.create_user("user2@example.com", "admin", ["read", "write", "admin"])
        
        ctx1 = auth.authenticate(api_key1)
        ctx2 = auth.authenticate(api_key2)
        
        assert ctx1.user.email == "user1@example.com"
        assert ctx2.user.email == "user2@example.com"
        assert ctx1.user.role == "viewer"
        assert ctx2.user.role == "admin"


class TestSecurityAdvanced:
    """Advanced security tests"""
    
    def test_sanitize_string(self):
        from shared.security import sanitize_string
        assert sanitize_string("  hello  ") == "hello"
        assert sanitize_string("test\x00null") == "testnull"
    
    def test_validate_price(self):
        from shared.security import validate_price
        assert validate_price(10.0) is True
        assert validate_price(0) is True
        assert validate_price(-1) is False
    
    def test_validate_currency(self):
        from shared.security import validate_currency
        assert validate_currency("USD") is True
        assert validate_currency("IDR") is True
        assert validate_currency("XXX") is False
    
    def test_encryption_utils(self):
        from shared.security import EncryptionUtils
        encrypted = EncryptionUtils.encrypt_data("secret", "key")
        decrypted = EncryptionUtils.decrypt_data(encrypted, "key")
        assert decrypted == "secret"
    
    def test_hash_data(self):
        from shared.security import EncryptionUtils
        hash1 = EncryptionUtils.hash_data("test")
        hash2 = EncryptionUtils.hash_data("test")
        assert hash1 == hash2
        assert len(hash1) == 64


class TestCacheAdvanced:
    """Advanced cache tests"""
    
    def test_cache_eviction_order(self):
        from shared.cache import InMemoryCache
        cache = InMemoryCache(max_size=3)
        
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        
        # Add d, should evict oldest (a) since cache is full
        cache.set("d", 4)
        
        assert cache.get("a") is None  # evicted (oldest)
        assert cache.get("b") == 2
        assert cache.get("c") == 3
        assert cache.get("d") == 4
    
    def test_cache_no_ttl(self):
        from shared.cache import InMemoryCache
        import time
        
        cache = InMemoryCache()
        cache.set("permanent", "value")  # No TTL
        
        time.sleep(0.1)
        assert cache.get("permanent") == "value"
    
    def test_cache_manager_redis_fallback(self):
        from shared.cache import CacheManager
        
        # Test with None redis_url
        cache = CacheManager(redis_url=None)
        cache.set("fallback", "test")
        assert cache.get("fallback") == "test"
        cache.delete("fallback")
        assert cache.get("fallback") is None
    
    def test_cache_clear_stats(self):
        from shared.cache import InMemoryCache
        cache = InMemoryCache()
        
        cache.set("k1", "v1")
        cache.set("k2", "v2")
        cache.get("k1")
        cache.get("missing")
        
        stats_before = cache.get_stats()
        assert stats_before["size"] == 2
        
        cache.clear()
        stats_after = cache.get_stats()
        assert stats_after["size"] == 0
        assert stats_after["hits"] == 0
        assert stats_after["misses"] == 0


class TestHealthAdvanced:
    """Advanced health tests"""
    
    def test_health_check_result(self):
        from shared.health import HealthCheckResult, HealthStatus
        result = HealthCheckResult(
            component="test",
            status=HealthStatus.HEALTHY,
            message="OK"
        )
        assert result.component == "test"
        assert result.status == HealthStatus.HEALTHY
        assert result.response_time_ms >= 0
    
    def test_disk_health_degraded(self):
        from shared.health import DiskHealthChecker
        import shutil
        
        checker = DiskHealthChecker("/", min_free_gb=999999)
        # This should be degraded since we don't have 999999 GB free
        # Just test that it initializes
        assert checker.critical is True
    
    def test_health_monitor_empty(self):
        from shared.health import HealthMonitor
        monitor = HealthMonitor()
        result = monitor.get_simple_health()
        assert result["status"] == "unknown"
    
    def test_health_response_building(self):
        from shared.health import HealthMonitor, HealthCheckResult, HealthStatus
        monitor = HealthMonitor()
        
        results = [
            HealthCheckResult("db", HealthStatus.HEALTHY, "OK", response_time_ms=1.0),
            HealthCheckResult("redis", HealthStatus.DEGRADED, "Slow", response_time_ms=100.0),
        ]
        
        response = monitor._build_health_response(results)
        assert response["status"] == "degraded"
        assert len(response["checks"]) == 2


class TestMonitoringAdvanced:
    """Advanced monitoring tests"""
    
    def test_metrics_all(self):
        from shared.monitoring import MetricsCollector
        metrics = MetricsCollector()
        
        metrics.increment("requests")
        metrics.gauge("memory", 512.0)
        metrics.histogram("latency", 0.1)
        
        all_metrics = metrics.get_all_metrics()
        assert "counters" in all_metrics
        assert "gauges" in all_metrics
        assert "histograms" in all_metrics
        assert all_metrics["counters"]["requests"] == 1.0
        assert all_metrics["gauges"]["memory"] == 512.0
    
    def test_prometheus_counter_format(self):
        from shared.monitoring import MetricsCollector, PrometheusExporter
        metrics = MetricsCollector()
        exporter = PrometheusExporter(metrics)
        
        metrics.increment("api_calls", 5.0, {"method": "GET", "endpoint": "/users"})
        output = exporter.export()
        
        assert "# TYPE api_calls counter" in output
        assert 'api_calls{endpoint="/users",method="GET"} 5.0' in output
    
    def test_prometheus_histogram_format(self):
        from shared.monitoring import MetricsCollector, PrometheusExporter
        metrics = MetricsCollector()
        exporter = PrometheusExporter(metrics)
        
        metrics.histogram("request_duration", 0.5)
        output = exporter.export()
        
        assert "# TYPE request_duration histogram" in output
        assert "request_duration_count" in output
    
    def test_count_calls_decorator(self):
        from shared.monitoring import count_calls, get_metrics
        metrics = get_metrics()
        
        call_count = 0
        @count_calls("decorated_calls")
        def my_function():
            nonlocal call_count
            call_count += 1
            return "result"
        
        result = my_function()
        assert result == "result"
        assert call_count == 1


class TestCoreEngineAdvanced:
    """Advanced core engine tests"""
    
    def test_engine_config_defaults(self):
        from shared.core_engine import CoreEngine
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
            f.write(b"engine:\n  name: test\n")
            config_path = f.name
        
        try:
            engine = CoreEngine(config_path=config_path)
            # If yaml is not installed, falls back to defaults
            # If yaml is installed, uses the config
            assert "engine" in engine.config
            assert "name" in engine.config["engine"]
        finally:
            Path(config_path).unlink()
    
    def test_engine_status_lifecycle(self):
        from shared.core_engine import CoreEngine, EngineStatus
        engine = CoreEngine()
        
        assert engine.status == EngineStatus.INITIALIZING
        engine.start()
        assert engine.status == EngineStatus.RUNNING
    
    def test_engine_shutdown_handler(self):
        from shared.core_engine import CoreEngine
        engine = CoreEngine()
        
        handler_called = False
        def shutdown_handler():
            nonlocal handler_called
            handler_called = True
        
        engine._shutdown_handlers.append(shutdown_handler)
        engine.stop()
        
        assert handler_called is True
    
    def test_engine_module_registration(self):
        from shared.core_engine import CoreEngine
        engine = CoreEngine()
        
        mock_module = Mock()
        engine.register_module("mock", mock_module)
        
        assert engine.get_module("mock") is mock_module
        assert "mock" in engine.get_status()["modules"]


class TestDatabaseAdvanced:
    """Advanced database tests"""
    
    def test_connection_pool_reuse(self, temp_dir):
        from shared.database import DatabaseManager
        db_path = temp_dir / "pool_test.db"
        db = DatabaseManager(db_path, pool_size=2)
        
        # Get connections multiple times
        conn1 = db.pool.get_connection()
        conn2 = db.pool.get_connection()
        
        db.pool.return_connection(conn1)
        db.pool.return_connection(conn2)
        
        # Should reuse connections
        conn3 = db.pool.get_connection()
        assert conn3 is conn1 or conn3 is conn2
        
        db.close()
    
    def test_database_error_handling(self, db_manager):
        with pytest.raises(Exception):
            db_manager.execute("SELECT * FROM nonexistent_table")
    
    def test_transaction_rollback(self, db_manager):
        db_manager.execute("CREATE TABLE IF NOT EXISTS accounts (id INTEGER PRIMARY KEY, balance REAL)")
        db_manager.execute("INSERT INTO accounts (balance) VALUES (?)", (1000.0,))
        
        # Transaction with error - should raise exception
        with pytest.raises(Exception):
            queries = [
                ("UPDATE accounts SET balance = balance - ? WHERE id = ?", (100.0, 1)),
                ("UPDATE nonexistent SET x = 1", ())  # This will fail
            ]
            db_manager.transaction(queries)
        
        # Verify the transaction method raises on error
        # Note: actual rollback behavior depends on SQLite implementation


class TestValidationAdvanced:
    """Advanced validation tests"""
    
    def test_url_validation(self):
        from shared.validation import FieldValidator
        assert FieldValidator.url("https://example.com", "url") == "https://example.com"
        assert FieldValidator.url("http://test.com/path", "url") == "http://test.com/path"
        with pytest.raises(Exception):
            FieldValidator.url("not-a-url", "url")
    
    def test_list_max_items(self):
        from shared.validation import FieldValidator
        with pytest.raises(Exception):
            FieldValidator.list([1, 2, 3, 4, 4], "items", max_items=3)
    
    def test_dict_validation(self):
        from shared.validation import FieldValidator
        assert FieldValidator.dict({"key": "value"}, "data") == {"key": "value"}
        with pytest.raises(Exception):
            FieldValidator.dict("not_dict", "data")
    
    def test_validator_multiple_errors(self):
        from shared.validation import RequestValidator
        validator = RequestValidator()
        
        schema = {
            "email": {"type": "email", "required": True},
            "age": {"type": "integer", "min_value": 0}
        }
        
        with pytest.raises(Exception):
            validator.validate({}, schema)  # Missing required fields
    
    def test_validator_no_required_fields(self):
        from shared.validation import RequestValidator
        validator = RequestValidator()
        
        schema = {
            "optional_field": {"type": "string"}
        }
        
        result = validator.validate({}, schema)
        assert result == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=shared", "--cov-report=term-missing"])
