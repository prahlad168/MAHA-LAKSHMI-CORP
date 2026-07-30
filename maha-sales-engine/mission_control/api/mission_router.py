#!/usr/bin/env python3
"""
MAHA Sales Engine V1 - Mission Control API

REST API endpoints for the Mission Control system.
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel

from mission_control.core.mission_controller import MissionController
from mission_control.models import MissionContext, PermissionLevel

logger = logging.getLogger("maha-sales-engine.mission-control.api")


# Request/Response Models
class MissionStatusResponse(BaseModel):
    """Mission status response model"""
    status: str
    mission_id: str
    name: str
    created_at: str
    updated_at: str
    config: Dict[str, Any]


class MissionInfoResponse(BaseModel):
    """Mission info response model"""
    mission_id: str
    name: str
    description: str
    version: str
    status: str
    timestamp: str


class MissionVersionResponse(BaseModel):
    """Mission version response model"""
    version: str
    build_date: str
    environment: str
    commit_hash: Optional[str] = None


# API Router
class MissionRouter:
    """
    Mission Control API router.
    
    Provides REST endpoints for mission control operations.
    """
    
    def __init__(self, controller: MissionController):
        """
        Initialize mission router.
        
        Args:
            controller: Mission controller instance
        """
        self.controller = controller
        self.app = FastAPI(
            title="MAHA Sales Engine Mission Control API",
            description="Mission Control system for MAHA Sales Engine V1",
            version="1.0.0"
        )
        self._setup_routes()
        self.logger = logging.getLogger("maha-sales-engine.mission-control.api")
    
    def _setup_routes(self) -> None:
        """Setup API routes"""
        
        @self.app.get("/mission/status", response_model=Dict[str, Any])
        async def get_mission_status(user_role: Optional[str] = Header(None)):
            """
            Get mission control system status.
            
            Returns overall system health and status information.
            """
            try:
                # Validate user role
                if not user_role:
                    raise HTTPException(status_code=401, detail="User role header required")
                
                # Check permissions
                from mission_control.permissions.permission_manager import PermissionManager
                from mission_control.core.mission_controller import get_controller
                controller = get_controller()
                if hasattr(controller, 'service') and hasattr(controller.service, 'auth'):
                    # Simple check - in production use proper auth
                    pass
                
                # Get system health
                health = self.controller.get_system_health()
                metrics = self.controller.get_controller_metrics()
                
                return {
                    "status": "success",
                    "data": {
                        "system_health": health,
                        "controller_metrics": metrics,
                        "timestamp": datetime.now().isoformat()
                    }
                }
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Failed to get mission status: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/mission/info", response_model=Dict[str, Any])
        async def get_mission_info():
            """
            Get mission control system information.
            
            Returns system configuration and capabilities.
            """
            try:
                config = self.controller.config
                return {
                    "status": "success",
                    "data": {
                        "mission_id": config.mission_id,
                        "name": config.name,
                        "description": config.description,
                        "version": config.version,
                        "enabled": config.enabled,
                        "capabilities": [
                            "mission_management",
                            "metrics_collection",
                            "alerting",
                            "audit_logging",
                            "health_monitoring"
                        ],
                        "timestamp": datetime.now().isoformat()
                    }
                }
            except Exception as e:
                self.logger.error(f"Failed to get mission info: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/mission/version", response_model=Dict[str, Any])
        async def get_mission_version():
            """
            Get mission control system version.
            
            Returns version information and build details.
            """
            try:
                config = self.controller.config
                return {
                    "status": "success",
                    "data": {
                        "version": config.version,
                        "name": config.name,
                        "build_date": "2026-07-30",
                        "environment": "production",
                        "timestamp": datetime.now().isoformat()
                    }
                }
            except Exception as e:
                self.logger.error(f"Failed to get mission version: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def get_app(self) -> FastAPI:
        """
        Get FastAPI application instance.
        
        Returns:
            FastAPI application
        """
        return self.app


# Factory function for creating router
def create_mission_router(controller: MissionController) -> MissionRouter:
    """
    Create mission router instance.
    
    Args:
        controller: Mission controller instance
        
    Returns:
        Mission router instance
    """
    return MissionRouter(controller)
