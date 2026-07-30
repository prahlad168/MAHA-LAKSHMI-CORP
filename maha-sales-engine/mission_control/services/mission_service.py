#!/usr/bin/env python3
"""
MAHA Sales Engine V1 - Mission Control Services

Business services for the Mission Control system.
"""

import sys
import json
import time
import logging
import secrets
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.core_engine import get_engine, EngineStatus
from shared.database import DatabaseManager
from shared.auth import AuthManager, UserRole, Permission
from mission_control.models import MissionContext, MissionConfig, MissionMetric, MissionAlert, MissionStatus

logger = logging.getLogger("maha-sales-engine.mission-control.services")


class MissionService:
    """
    Core business service for Mission Control operations.
    
    Orchestrates mission control workflows, integrates with
    existing MAHA Sales Engine modules, and provides business
    logic for executive oversight.
    """
    
    def __init__(self, config: MissionConfig, db_manager: DatabaseManager, auth_manager: AuthManager):
        """
        Initialize mission service.
        
        Args:
            config: Mission Control configuration
            db_manager: Database manager instance
            auth_manager: Authentication manager instance
        """
        self.config = config
        self.db = db_manager
        self.auth = auth_manager
        self.engine = get_engine()
        self._active_missions: Dict[str, MissionContext] = {}
        self._metrics_cache: Dict[str, List[MissionMetric]] = {}
        self._setup_service()
    
    def _setup_service(self) -> None:
        """Setup service components"""
        try:
            self.engine.register_module("mission_control", self)
            logger.info("Mission Control service registered with core engine")
        except Exception as e:
            logger.error(f"Failed to register mission control service: {e}")
            raise
    
    def create_mission(self, context: MissionContext, mission_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new mission.
        
        Args:
            context: Mission context with user information
            mission_config: Mission configuration parameters
            
        Returns:
            Mission creation result
        """
        try:
            mission_id = context.mission_id
            self._active_missions[mission_id] = context
            
            logger.info(f"Creating mission: {mission_id}")
            
            # Validate permissions
            if not self._check_permission(context, "create"):
                raise PermissionError(f"User {context.user_id} lacks permission to create missions")
            
            # Create mission record
            from mission_control.repositories.mission_repository import MissionRepository, MissionRecord
            repo = MissionRepository(self.db)
            
            mission = MissionRecord(
                mission_id=mission_id,
                name=mission_config.get("name", f"Mission {mission_id}"),
                status=MissionStatus.INITIALIZING.value,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                config=mission_config
            )
            
            if not repo.create_mission(mission):
                raise RuntimeError(f"Failed to create mission record: {mission_id}")
            
            return {
                "mission_id": mission_id,
                "status": MissionStatus.INITIALIZING.value,
                "message": "Mission created successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to create mission {context.mission_id}: {e}")
            return {
                "mission_id": context.mission_id,
                "status": MissionStatus.ERROR.value,
                "error": str(e)
            }
    
    def get_mission_status(self, mission_id: str) -> Dict[str, Any]:
        """
        Get mission status.
        
        Args:
            mission_id: Mission identifier
            
        Returns:
            Mission status information
        """
        try:
            from mission_control.repositories.mission_repository import MissionRepository
            repo = MissionRepository(self.db)
            mission = repo.get_mission(mission_id)
            
            if not mission:
                return {"error": f"Mission {mission_id} not found"}
            
            return {
                "mission_id": mission.mission_id,
                "name": mission.name,
                "status": mission.status,
                "created_at": mission.created_at,
                "updated_at": mission.updated_at,
                "config": mission.config
            }
        except Exception as e:
            logger.error(f"Failed to get mission status {mission_id}: {e}")
            return {"error": str(e)}
    
    def list_active_missions(self) -> List[Dict[str, Any]]:
        """
        List all active missions.
        
        Returns:
            List of active mission information
        """
        try:
            from mission_control.repositories.mission_repository import MissionRepository
            repo = MissionRepository(self.db)
            missions = repo.list_missions(status=MissionStatus.RUNNING.value)
            
            return [
                {
                    "mission_id": m.mission_id,
                    "name": m.name,
                    "status": m.status,
                    "created_at": m.created_at,
                    "updated_at": m.updated_at
                }
                for m in missions
            ]
        except Exception as e:
            logger.error(f"Failed to list active missions: {e}")
            return []
    
    def record_metric(self, mission_id: str, metric: MissionMetric) -> bool:
        """
        Record a metric for a mission.
        
        Args:
            mission_id: Mission identifier
            metric: Metric to record
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from mission_control.repositories.mission_repository import MissionRepository
            repo = MissionRepository(self.db)
            return repo.record_metric(metric)
        except Exception as e:
            logger.error(f"Failed to record metric for mission {mission_id}: {e}")
            return False
    
    def record_alert(self, mission_id: str, alert: MissionAlert) -> bool:
        """
        Record an alert for a mission.
        
        Args:
            mission_id: Mission identifier
            alert: Alert to record
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from mission_control.repositories.mission_repository import MissionRepository
            repo = MissionRepository(self.db)
            return repo.record_alert(alert)
        except Exception as e:
            logger.error(f"Failed to record alert for mission {mission_id}: {e}")
            return False
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        Get overall system health status.
        
        Returns:
            System health information
        """
        try:
            health_status = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "services": {},
                "metrics": {
                    "active_missions": len(self._active_missions),
                    "total_missions": len(self._get_all_missions()),
                    "system_uptime": self._get_uptime()
                }
            }
            
            # Check core engine health
            if self.engine:
                health_status["services"]["core_engine"] = {
                    "status": "running" if self.engine.status == EngineStatus.RUNNING else "error",
                    "modules": len(self.engine.modules)
                }
            
            # Check database health
            try:
                self.db.execute_query("SELECT 1")
                health_status["services"]["database"] = {"status": "healthy"}
            except Exception as e:
                health_status["services"]["database"] = {"status": "error", "message": str(e)}
                health_status["status"] = "degraded"
            
            # Check auth manager health
            if self.auth:
                health_status["services"]["auth"] = {"status": "running" if self.auth._api_keys else "warning"}
            
            return health_status
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _check_permission(self, context: MissionContext, action: str) -> bool:
        """
        Check if user has permission for action.
        
        Args:
            context: Mission context
            action: Action to check permission for
            
        Returns:
            True if authorized, False otherwise
        """
        try:
            required_permissions = {
                "create": [Permission.WRITE, Permission.ADMIN],
                "read": [Permission.READ, Permission.WRITE, Permission.ADMIN],
                "update": [Permission.WRITE, Permission.ADMIN],
                "delete": [Permission.ADMIN],
                "admin": [Permission.ADMIN]
            }
            
            required = required_permissions.get(action, [Permission.ADMIN])
            user_permissions = [Permission(p) for p in context.metadata.get("permissions", [])]
            
            return any(perm in user_permissions for perm in required)
        except Exception as e:
            logger.error(f"Permission check failed: {e}")
            return False
    
    def _get_all_missions(self) -> List[str]:
        """Get all mission IDs"""
        try:
            from mission_control.repositories.mission_repository import MissionRepository
            repo = MissionRepository(self.db)
            missions = repo.list_missions(limit=1000)
            return [m.mission_id for m in missions]
        except Exception:
            return list(self._active_missions.keys())
    
    def _get_uptime(self) -> str:
        """Get system uptime"""
        try:
            uptime_seconds = (datetime.now() - self.engine._start_time).total_seconds()
            hours = int(uptime_seconds // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
        except Exception:
            return "unknown"
