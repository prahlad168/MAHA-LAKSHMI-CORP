#!/usr/bin/env python3
"""
MAHA Sales Engine V1 - Mission Control Health Monitoring Integration

Integrates Mission Control with the existing Health Monitoring system.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.health import HealthChecker, HealthStatus, HealthCheckResult
from shared.logging_utils import get_logger
from mission_control.models import MissionContext

logger = get_logger("maha-sales-engine.mission-control.health")


class MissionControlHealthChecker(HealthChecker):
    """Mission Control health checker"""
    
    def __init__(self, mission_controller):
        super().__init__("mission_control", critical=True)
        self.mission_controller = mission_controller
    
    async def _check(self) -> tuple:
        try:
            health = self.mission_controller.get_system_health()
            status = health.get("status", "unknown")
            
            if status == "healthy":
                return HealthStatus.HEALTHY, "Mission Control healthy", health
            elif status == "degraded":
                return HealthStatus.DEGRADED, "Mission Control degraded", health
            else:
                return HealthStatus.UNHEALTHY, f"Mission Control unhealthy: {health.get('error', 'unknown')}", health
        except Exception as e:
            return HealthStatus.UNHEALTHY, f"Health check failed: {e}", {}


class HealthMonitoringIntegration:
    """
    Integrates Mission Control with the Health Monitoring system.
    
    Registers Mission Control health checks with the shared
    health monitoring system and provides unified health status.
    """
    
    def __init__(self, mission_controller, health_monitor=None):
        """
        Initialize health monitoring integration.
        
        Args:
            mission_controller: Mission controller instance
            health_monitor: Optional existing health monitor instance
        """
        self.mission_controller = mission_controller
        self.health_monitor = health_monitor
        self._checker = MissionControlHealthChecker(mission_controller)
        self.logger = get_logger("maha-sales-engine.mission-control.health")
    
    def register_with_health_monitor(self) -> None:
        """Register Mission Control with existing health monitor"""
        try:
            if self.health_monitor:
                self.health_monitor.register_component("mission_control")
                self.logger.info("Registered mission_control with health monitor")
            else:
                self.logger.warning("Health monitor not available")
        except Exception as e:
            self.logger.error(f"Failed to register with health monitor: {e}")
    
    def check_health(self) -> Dict[str, Any]:
        """
        Perform Mission Control health check.
        
        Returns:
            Health check result
        """
        try:
            health = self.mission_controller.get_system_health()
            
            # Map to shared health format
            status_map = {
                "healthy": HealthStatus.HEALTHY,
                "degraded": HealthStatus.DEGRADED,
                "error": HealthStatus.UNHEALTHY
            }
            
            status = status_map.get(health.get("status", "unknown"), HealthStatus.UNKNOWN)
            
            return {
                "component": "mission_control",
                "status": status.value,
                "message": health.get("status", "unknown"),
                "details": health,
                "checked_at": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "component": "mission_control",
                "status": HealthStatus.UNHEALTHY.value,
                "message": str(e),
                "details": {},
                "checked_at": datetime.now().isoformat()
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get comprehensive health status.
        
        Returns:
            Health status dictionary
        """
        try:
            controller_health = self.check_health()
            controller_metrics = self.mission_controller.get_controller_metrics()
            
            return {
                "mission_control": controller_health,
                "metrics": controller_metrics,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to get health status: {e}")
            return {
                "mission_control": {
                    "status": "error",
                    "error": str(e)
                },
                "timestamp": datetime.now().isoformat()
            }
