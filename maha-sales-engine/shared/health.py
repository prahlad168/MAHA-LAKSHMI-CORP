#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Health Check System
Comprehensive health monitoring for all services and dependencies.
"""

import os
import sys
import json
import time
import socket
import logging
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.health")


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    component: str
    status: HealthStatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    checked_at: str = field(default_factory=lambda: datetime.now().isoformat())
    response_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "component": self.component,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "checked_at": self.checked_at,
            "response_time_ms": self.response_time_ms
        }


class HealthChecker:
    """Base health checker"""
    
    def __init__(self, name: str, critical: bool = True):
        self.name = name
        self.critical = critical
    
    async def check(self) -> HealthCheckResult:
        """Perform health check"""
        start = time.time()
        try:
            status, message, details = await self._check()
            response_time = (time.time() - start) * 1000
            return HealthCheckResult(
                component=self.name,
                status=status,
                message=message,
                details=details,
                response_time_ms=response_time
            )
        except Exception as e:
            response_time = (time.time() - start) * 1000
            logger.error(f"Health check failed for {self.name}: {e}")
            return HealthCheckResult(
                component=self.name,
                status=HealthStatus.UNHEALTHY,
                message=str(e),
                response_time_ms=response_time
            )
    
    async def _check(self) -> tuple:
        """Override in subclass"""
        return HealthStatus.HEALTHY, "OK", {}


class DatabaseHealthChecker(HealthChecker):
    """Database health checker"""
    
    def __init__(self, db_manager):
        super().__init__("database", critical=True)
        self.db = db_manager
    
    async def _check(self) -> tuple:
        try:
            with self.db.get_connection() as conn:
                result = conn.execute("SELECT 1").fetchone()
                if result and result[0] == 1:
                    return HealthStatus.HEALTHY, "Database connection OK", {
                        "pool_size": getattr(self.db.pool, 'max_connections', 'N/A'),
                        "active_connections": getattr(self.db.pool, '_created_connections', 'N/A')
                    }
                return HealthStatus.UNHEALTHY, "Database query failed", {}
        except Exception as e:
            return HealthStatus.UNHEALTHY, f"Database error: {e}", {}


class RedisHealthChecker(HealthChecker):
    """Redis health checker"""
    
    def __init__(self, redis_client=None):
        super().__init__("redis", critical=False)
        self.redis = redis_client
    
    async def _check(self) -> tuple:
        if not self.redis:
            return HealthStatus.UNKNOWN, "Redis not configured", {}
        
        try:
            self.redis.ping()
            info = self.redis.info()
            return HealthStatus.HEALTHY, "Redis connection OK", {
                "version": info.get("redis_version"),
                "connected_clients": info.get("connected_clients")
            }
        except Exception as e:
            return HealthStatus.UNHEALTHY, f"Redis error: {e}", {}


class DiskHealthChecker(HealthChecker):
    """Disk space health checker"""
    
    def __init__(self, path: str = "/", min_free_gb: float = 10.0):
        super().__init__("disk", critical=True)
        self.path = path
        self.min_free_gb = min_free_gb
    
    async def _check(self) -> tuple:
        try:
            import shutil
            usage = shutil.disk_usage(self.path)
            free_gb = usage.free / (1024**3)
            
            if free_gb < self.min_free_gb:
                return HealthStatus.DEGRADED, f"Low disk space: {free_gb:.2f} GB free", {
                    "free_gb": round(free_gb, 2),
                    "total_gb": round(usage.total / (1024**3), 2),
                    "used_percent": round((usage.used / usage.total) * 100, 2)
                }
            
            return HealthStatus.HEALTHY, f"Disk OK: {free_gb:.2f} GB free", {
                "free_gb": round(free_gb, 2),
                "total_gb": round(usage.total / (1024**3), 2),
                "used_percent": round((usage.used / usage.total) * 100, 2)
            }
        except Exception as e:
            return HealthStatus.UNHEALTHY, f"Disk check error: {e}", {}


class MemoryHealthChecker(HealthChecker):
    """Memory health checker"""
    
    def __init__(self, max_usage_percent: float = 90.0):
        super().__init__("memory", critical=True)
        self.max_usage_percent = max_usage_percent
    
    async def _check(self) -> tuple:
        try:
            import psutil
            memory = psutil.virtual_memory()
            
            if memory.percent > self.max_usage_percent:
                return HealthStatus.DEGRADED, f"High memory usage: {memory.percent}%", {
                    "usage_percent": memory.percent,
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2)
                }
            
            return HealthStatus.HEALTHY, f"Memory OK: {memory.percent}% used", {
                "usage_percent": memory.percent,
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2)
            }
        except ImportError:
            return HealthStatus.UNKNOWN, "psutil not installed", {}
        except Exception as e:
            return HealthStatus.UNHEALTHY, f"Memory check error: {e}", {}


class CPUHealthChecker(HealthChecker):
    """CPU health checker"""
    
    def __init__(self, max_usage_percent: float = 90.0):
        super().__init__("cpu", critical=False)
        self.max_usage_percent = max_usage_percent
    
    async def _check(self) -> tuple:
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            
            if cpu_percent > self.max_usage_percent:
                return HealthStatus.DEGRADED, f"High CPU usage: {cpu_percent}%", {
                    "usage_percent": cpu_percent,
                    "core_count": psutil.cpu_count()
                }
            
            return HealthStatus.HEALTHY, f"CPU OK: {cpu_percent}%", {
                "usage_percent": cpu_percent,
                "core_count": psutil.cpu_count()
            }
        except ImportError:
            return HealthStatus.UNKNOWN, "psutil not installed", {}
        except Exception as e:
            return HealthStatus.UNHEALTHY, f"CPU check error: {e}", {}


class HealthMonitor:
    """Central health monitoring system"""
    
    def __init__(self):
        self._checkers: List[HealthChecker] = []
        self._last_check: Optional[List[HealthCheckResult]] = None
        self._check_interval = 30
        self._running = False
        self._thread: Optional[threading.Thread] = None
    
    def register_checker(self, checker: HealthChecker):
        """Register health checker"""
        self._checkers.append(checker)
        logger.info(f"Health checker registered: {checker.name}")
    
    async def check_all(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = []
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(self._run_check, checker): checker for checker in self._checkers}
            
            for future in as_completed(futures):
                checker = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append(HealthCheckResult(
                        component=checker.name,
                        status=HealthStatus.UNHEALTHY,
                        message=f"Check failed: {e}"
                    ))
        
        self._last_check = results
        return self._build_health_response(results)
    
    def _run_check(self, checker: HealthChecker):
        """Run single check"""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(checker.check())
        finally:
            loop.close()
    
    def _build_health_response(self, results: List[HealthCheckResult]) -> Dict[str, Any]:
        """Build health response"""
        status = HealthStatus.HEALTHY
        
        for result in results:
            if result.status == HealthStatus.UNHEALTHY and result.critical:
                status = HealthStatus.UNHEALTHY
            elif result.status == HealthStatus.DEGRADED and status != HealthStatus.UNHEALTHY:
                status = HealthStatus.DEGRADED
        
        return {
            "status": status.value,
            "timestamp": datetime.now().isoformat(),
            "checks": [
                {
                    "component": r.component,
                    "status": r.status.value,
                    "message": r.message,
                    "response_time_ms": r.response_time_ms,
                    "details": r.details
                }
                for r in results
            ]
        }
    
    def get_simple_health(self) -> Dict[str, str]:
        """Get simple health status"""
        if not self._last_check:
            return {"status": HealthStatus.UNKNOWN.value}
        
        status = HealthStatus.HEALTHY
        for result in self._last_check:
            if result.status == HealthStatus.UNHEALTHY and result.critical:
                status = HealthStatus.UNHEALTHY
            elif result.status == HealthStatus.DEGRADED and status != HealthStatus.UNHEALTHY:
                status = HealthStatus.DEGRADED
        
        return {"status": status.value}


# Global health monitor
health_monitor = HealthMonitor()


def get_health_monitor() -> HealthMonitor:
    """Get global health monitor"""
    return health_monitor


def main():
    """Test health check system"""
    monitor = HealthMonitor()
    
    # Register checkers
    monitor.register_checker(DiskHealthChecker("/", min_free_gb=1.0))
    monitor.register_checker(MemoryHealthChecker())
    monitor.register_checker(CPUHealthChecker())
    
    print("Health check system loaded")


if __name__ == "__main__":
    main()
