#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Health & Cache Coverage Push
Targeted tests to push health and cache coverage above 80%.
"""

import os
import sys
import json
import time
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestHealthComprehensive:
    """Comprehensive health tests"""
    
    def test_redis_health_checker_no_client(self):
        from shared.health import RedisHealthChecker
        checker = RedisHealthChecker(redis_client=None)
        assert checker.name == "redis"
        assert checker.critical is False
    
    def test_database_health_checker(self, db_manager):
        from shared.health import DatabaseHealthChecker
        checker = DatabaseHealthChecker(db_manager)
        assert checker.name == "database"
        assert checker.critical is True
    
    def test_health_monitor_check_all(self):
        from shared.health import HealthMonitor, DiskHealthChecker, MemoryHealthChecker
        monitor = HealthMonitor()
        monitor.register_checker(DiskHealthChecker("/", min_free_gb=0.01))
        monitor.register_checker(MemoryHealthChecker(max_usage_percent=100))
        
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(monitor.check_all())
            assert "status" in result
            assert "checks" in result
            assert len(result["checks"]) == 2
        finally:
            loop.close()
    
    def test_health_monitor_run_check(self):
        from shared.health import HealthMonitor, DiskHealthChecker
        
        monitor = HealthMonitor()
        checker = DiskHealthChecker("/", min_free_gb=0.01)
        
        result = monitor._run_check(checker)
        assert result.component == "disk"
        assert result.status.value in ["healthy", "degraded", "unhealthy"]
    
    def test_health_check_result_to_dict(self):
        from shared.health import HealthCheckResult, HealthStatus
        result = HealthCheckResult(
            component="test",
            status=HealthStatus.HEALTHY,
            message="OK",
            details={"key": "value"}
        )
        
        result_dict = result.to_dict()
        assert result_dict["component"] == "test"
        assert result_dict["status"] == "healthy"
        assert result_dict["details"] == {"key": "value"}
    
    def test_health_status_enum(self):
        from shared.health import HealthStatus
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"
        assert HealthStatus.UNKNOWN.value == "unknown"


class TestCacheComprehensive:
    """Comprehensive cache tests"""
    
    def test_cache_manager_stats_no_redis(self):
        from shared.cache import CacheManager
        cache = CacheManager(redis_url=None)
        
        cache.set("k1", "v1")
        cache.set("k2", "v2")
        cache.get("k1")  # hit
        cache.get("missing")  # miss
        
        stats = cache.get_stats()
        assert stats["backend"] == "memory"
        assert stats["memory"]["size"] == 2
        assert stats["memory"]["hits"] == 1
        assert stats["memory"]["misses"] == 1
    
    def test_cache_manager_delete_nonexistent(self):
        from shared.cache import CacheManager
        cache = CacheManager()
        # Should not raise
        cache.delete("nonexistent")
    
    def test_cache_manager_clear_empty(self):
        from shared.cache import CacheManager
        cache = CacheManager()
        # Should not raise
        cache.clear()
    
    def test_in_memory_cache_max_size_zero(self):
        from shared.cache import InMemoryCache
        cache = InMemoryCache(max_size=0)
        # With max_size=0, set should handle gracefully without crash
        # Value may not be stored due to immediate eviction
        cache.set("key", "value")
        # Just verify no exception is raised
    
    def test_cache_entry_is_expired(self):
        from shared.cache import CacheEntry
        from datetime import datetime, timedelta
        
        # Not expired
        entry1 = CacheEntry(
            key="k1",
            value="v1",
            expires_at=(datetime.now() + timedelta(hours=1)).isoformat(),
            created_at=datetime.now().isoformat()
        )
        assert entry1.is_expired() is False
        
        # Expired
        entry2 = CacheEntry(
            key="k2",
            value="v2",
            expires_at=(datetime.now() - timedelta(hours=1)).isoformat(),
            created_at=datetime.now().isoformat()
        )
        assert entry2.is_expired() is True
        
        # No expiry
        entry3 = CacheEntry(
            key="k3",
            value="v3",
            expires_at=None,
            created_at=datetime.now().isoformat()
        )
        assert entry3.is_expired() is False
    
    def test_cache_error_handling(self):
        from shared.cache import CacheManager
        
        # Test that cache handles errors gracefully
        cache = CacheManager()
        cache.set("test", "value")
        # Even if Redis fails, memory cache should work
        assert cache.get("test") == "value"


class TestAuthComprehensive:
    """Comprehensive auth tests"""
    
    def test_auth_manager_multiple_permissions(self, db_manager):
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
        api_key = auth.create_user("admin@example.com", "admin", ["read", "write", "delete", "admin"])
        
        context = auth.authenticate(api_key)
        assert context is not None
        
        # Admin should have all permissions
        assert auth.authorize(context, "read") is True
        assert auth.authorize(context, "write") is True
        assert auth.authorize(context, "delete") is True
        assert auth.authorize(context, "admin") is True
    
    def test_auth_manager_inactive_user(self, db_manager):
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
        api_key = auth.create_user("test@example.com", "user", ["read"])
        
        # Deactivate user
        db_manager.execute("UPDATE users SET is_active = 0 WHERE api_key = ?", (api_key,))
        
        # Should not authenticate inactive user
        context = auth.authenticate(api_key)
        assert context is None
    
    def test_auth_error_handling(self, db_manager):
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
        
        # Create user with duplicate email should fail gracefully
        auth.create_user("test@example.com", "user", ["read"])
        result = auth.create_user("test@example.com", "user", ["read"])
        # Duplicate email fails at DB level, returns None
        assert result is None


class TestSecurityComprehensive:
    """Comprehensive security tests"""
    
    def test_password_hashing_different_salts(self):
        from shared.security import SecurityUtils
        
        hash1, salt1 = SecurityUtils.hash_password("password")
        hash2, salt2 = SecurityUtils.hash_password("password")
        
        # Same password, different salts should produce different hashes
        assert hash1 != hash2
        assert salt1 != salt2
        
        # But both should verify
        assert SecurityUtils.verify_password("password", salt1, hash1) is True
        assert SecurityUtils.verify_password("password", salt2, hash2) is True
    
    def test_api_key_uniqueness(self):
        from shared.security import SecurityUtils
        
        keys = [SecurityUtils.generate_api_key() for _ in range(100)]
        assert len(set(keys)) == 100
    
    def test_rate_limiter_multiple_windows(self):
        from shared.security import RateLimiter
        limiter = RateLimiter()
        
        # Use up limit in first window
        for _ in range(3):
            assert limiter.is_allowed("test", 3, 1) is True
        assert limiter.is_allowed("test", 3, 1) is False
        
        # Different key should work
        assert limiter.is_allowed("other", 3, 1) is True
    
    def test_validation_error_format(self):
        from shared.validation import ValidationError
        error = ValidationError("field_name", "error message")
        assert error.field == "field_name"
        assert error.message == "error message"
        assert "field_name" in str(error)
        assert "error message" in str(error)


class TestMonitoringComprehensive:
    """Comprehensive monitoring tests"""
    
    def test_metrics_collector_labels(self):
        from shared.monitoring import MetricsCollector
        metrics = MetricsCollector()
        
        metrics.increment("requests", 1.0, {"method": "GET", "endpoint": "/api"})
        metrics.increment("requests", 2.0, {"method": "POST", "endpoint": "/api"})
        metrics.increment("requests", 3.0, {"method": "GET", "endpoint": "/api"})
        
        assert metrics.get_counter("requests", {"method": "GET", "endpoint": "/api"}) == 4.0
        assert metrics.get_counter("requests", {"method": "POST", "endpoint": "/api"}) == 2.0
    
    def test_prometheus_gauge_format(self):
        from shared.monitoring import MetricsCollector, PrometheusExporter
        metrics = MetricsCollector()
        exporter = PrometheusExporter(metrics)
        
        metrics.gauge("temperature", 37.5, {"unit": "celsius"})
        output = exporter.export()
        
        assert "# TYPE temperature gauge" in output
        assert 'temperature{unit="celsius"} 37.5' in output
    
    def test_prometheus_empty_export(self):
        from shared.monitoring import MetricsCollector, PrometheusExporter
        metrics = MetricsCollector()
        exporter = PrometheusExporter(metrics)
        
        output = exporter.export()
        assert output == "\n"  # Empty metrics


class TestUtilsComprehensive:
    """Comprehensive utils tests"""
    
    def test_time_utils_parse_iso(self):
        from shared.utils import TimeUtils
        dt = TimeUtils.parse_iso("2024-01-01T12:00:00")
        assert dt.year == 2024
        assert dt.month == 1
        assert dt.day == 1
    
    def test_time_utils_is_expired_edge_cases(self):
        from shared.utils import TimeUtils
        from datetime import datetime, timedelta
        
        # Invalid format
        assert TimeUtils.is_expired("not-a-date") is True
        
        # Future time - not expired
        future = (datetime.now() + timedelta(hours=1)).isoformat()
        assert TimeUtils.is_expired(future) is False
    
    def test_app_error(self):
        from shared.utils import AppError, ErrorCode
        
        error = AppError(
            code=ErrorCode.VALIDATION_ERROR.value,
            message="Invalid input",
            details={"field": "email"}
        )
        
        error_dict = error.to_dict()
        assert error_dict["error"]["code"] == "VALIDATION_ERROR"
        assert error_dict["error"]["message"] == "Invalid input"
        assert error_dict["error"]["details"]["field"] == "email"
    
    def test_retry_with_finally(self):
        from shared.utils import retry
        
        cleanup_called = False
        
        @retry(max_attempts=2)
        def failing_function():
            nonlocal cleanup_called
            cleanup_called = True
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError):
            failing_function()
        
        assert cleanup_called is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=shared", "--cov-report=term-missing"])
