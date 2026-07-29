#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Health Monitor
System health monitoring and alerting.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.sales-automation.health")


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ComponentHealth:
    """Health status for a component"""
    
    def __init__(self, name: str):
        self.name = name
        self.status = HealthStatus.UNKNOWN.value
        self.uptime = 0
        self.last_check = None
        self.error_message = None
        self.metrics: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "uptime": self.uptime,
            "last_check": self.last_check,
            "error_message": self.error_message,
            "metrics": self.metrics
        }


class HealthMonitor:
    """Monitor system health"""
    
    def __init__(self, db_manager, event_bus):
        self.db = db_manager
        self.event_bus = event_bus
        self._components: Dict[str, ComponentHealth] = {}
    
    def register_component(self, name: str):
        self._components[name] = ComponentHealth(name)
    
    def check_health(self, component_name: str) -> Dict[str, Any]:
        component = self._components.get(component_name)
        if not component:
            return {"status": "unknown", "error": "Component not found"}
        
        try:
            component.last_check = datetime.now().isoformat()
            component.status = HealthStatus.HEALTHY.value
            return component.to_dict()
        except Exception as e:
            component.status = HealthStatus.UNHEALTHY.value
            component.error_message = str(e)
            return component.to_dict()
    
    def get_overall_health(self) -> Dict[str, Any]:
        components = []
        healthy_count = 0
        unhealthy_count = 0
        
        for name, component in self._components.items():
            health = self.check_health(name)
            components.append(health)
            if health["status"] == HealthStatus.HEALTHY.value:
                healthy_count += 1
            else:
                unhealthy_count += 1
        
        overall = HealthStatus.HEALTHY.value
        if unhealthy_count > 0:
            overall = HealthStatus.DEGRADED.value
        if unhealthy_count > len(self._components) / 2:
            overall = HealthStatus.UNHEALTHY.value
        
        return {
            "status": overall,
            "healthy_count": healthy_count,
            "unhealthy_count": unhealthy_count,
            "total_count": len(self._components),
            "components": components
        }


def main():
    print("Health Monitor initialized")


if __name__ == "__main__":
    main()
