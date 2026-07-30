#!/usr/bin/env python3
"""
MAHA Sales Engine V1 - Mission Control Models

Data models and schemas for the Mission Control system.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.core_engine import EngineStatus


class MissionStatus(Enum):
    """Mission Control system status"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class PermissionLevel(Enum):
    """Permission levels for Mission Control access"""
    CEO = "ceo"
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


@dataclass
class MissionContext:
    """
    Context object for Mission Control operations.
    
    Contains all necessary information for processing
    mission control requests and maintaining state.
    """
    mission_id: str
    user_id: str
    permission_level: PermissionLevel
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary"""
        return {
            "mission_id": self.mission_id,
            "user_id": self.user_id,
            "permission_level": self.permission_level.value,
            "timestamp": self.timestamp,
            "session_id": self.session_id,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MissionContext":
        """Create context from dictionary"""
        return cls(
            mission_id=data["mission_id"],
            user_id=data["user_id"],
            permission_level=PermissionLevel(data["permission_level"]),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            session_id=data.get("session_id"),
            metadata=data.get("metadata", {})
        )


@dataclass
class MissionConfig:
    """
    Configuration for Mission Control system.
    
    Loads and validates configuration from various sources
    including files, environment variables, and defaults.
    """
    mission_id: str
    name: str
    description: str
    version: str = "1.0.0"
    enabled: bool = True
    max_concurrent_operations: int = 10
    timeout_seconds: int = 30
    retry_attempts: int = 3
    retry_delay_seconds: int = 5
    allowed_permissions: list = field(default_factory=lambda: ["ceo", "admin", "operator", "viewer"])
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if not self.mission_id:
            raise ValueError("mission_id is required")
        if not self.name:
            raise ValueError("name is required")
        if self.max_concurrent_operations < 1:
            raise ValueError("max_concurrent_operations must be >= 1")
        if self.timeout_seconds < 1:
            raise ValueError("timeout_seconds must be >= 1")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "mission_id": self.mission_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "enabled": self.enabled,
            "max_concurrent_operations": self.max_concurrent_operations,
            "timeout_seconds": self.timeout_seconds,
            "retry_attempts": self.retry_attempts,
            "retry_delay_seconds": self.retry_delay_seconds,
            "allowed_permissions": self.allowed_permissions,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MissionConfig":
        """Create config from dictionary"""
        return cls(
            mission_id=data["mission_id"],
            name=data["name"],
            description=data["description"],
            version=data.get("version", "1.0.0"),
            enabled=data.get("enabled", True),
            max_concurrent_operations=data.get("max_concurrent_operations", 10),
            timeout_seconds=data.get("timeout_seconds", 30),
            retry_attempts=data.get("retry_attempts", 3),
            retry_delay_seconds=data.get("retry_delay_seconds", 5),
            allowed_permissions=data.get("allowed_permissions", ["ceo", "admin", "operator", "viewer"]),
            metadata=data.get("metadata", {})
        )


@dataclass
class MissionMetric:
    """
    Metric data point for Mission Control monitoring.
    """
    metric_id: str
    name: str
    value: float
    unit: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary"""
        return {
            "metric_id": self.metric_id,
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp,
            "tags": self.tags
        }


@dataclass
class MissionAlert:
    """
    Alert data for Mission Control notification system.
    """
    alert_id: str
    severity: str  # critical, warning, info
    message: str
    source: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    acknowledged: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary"""
        return {
            "alert_id": self.alert_id,
            "severity": self.severity,
            "message": self.message,
            "source": self.source,
            "timestamp": self.timestamp,
            "acknowledged": self.acknowledged,
            "metadata": self.metadata
        }
