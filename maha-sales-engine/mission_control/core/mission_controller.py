#!/usr/bin/env python3
"""
MAHA Sales Engine V1 - Mission Control Core

Core business logic and orchestration for the Mission Control system.
"""

import sys
import os
import json
import time
import logging
import secrets
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.core_engine import get_engine
from shared.database import DatabaseManager
from shared.auth import AuthManager, UserRole
from mission_control.models import MissionContext, MissionConfig, MissionStatus, PermissionLevel
from mission_control.services.mission_service import MissionService

logger = logging.getLogger("maha-sales-engine.mission-control.core")


class MissionControllerError(Exception):
    """Mission Control controller error"""
    pass


class MissionController:
    """
    Main controller for Mission Control system.
    
    Orchestrates mission control operations, manages context,
    and coordinates between services and repositories.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize mission controller.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.engine = get_engine()
        self.config = self._load_config(config_path)
        self.db = self._initialize_database()
        self.auth = self._initialize_auth()
        self.service = self._initialize_service()
        self._start_time = datetime.now()
        self._operation_count = 0
        self._setup_controller()
        self.integrations = self._setup_integrations()
    
    def _setup_integrations(self):
        """Setup integration manager"""
        try:
            from mission_control.integrations.manager import IntegrationManager
            return IntegrationManager(self)
        except Exception as e:
            logger.error(f"Failed to setup integrations: {e}")
            return None
    
    def _load_config(self, config_path: Optional[str]) -> MissionConfig:
        """Load and validate configuration"""
        try:
            if not config_path:
                config_path = os.environ.get("MISSION_CONTROL_CONFIG", "config/mission_control.yaml")
            
            config_path = Path(config_path)
            if config_path.exists():
                import yaml
                with open(config_path) as f:
                    config_data = yaml.safe_load(f)
                logger.info(f"Mission Control configuration loaded from {config_path}")
                return MissionConfig.from_dict(config_data)
            else:
                logger.warning("Config file not found, using defaults")
                return self._get_default_config()
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise MissionControllerError(f"Configuration loading failed: {e}")
    
    def _get_default_config(self) -> MissionConfig:
        """Get default configuration"""
        return MissionConfig(
            mission_id="mission-control-default",
            name="Mission Control",
            description="MAHA Sales Engine Mission Control System",
            version="1.0.0",
            enabled=True,
            max_concurrent_operations=10,
            timeout_seconds=30,
            retry_attempts=3,
            retry_delay_seconds=5
        )
    
    def _initialize_database(self) -> DatabaseManager:
        """Initialize database connection"""
        try:
            db_path = self.config.metadata.get("database_path", "data/mission_control.db")
            db_manager = DatabaseManager(db_path)
            logger.info("Mission Control database initialized")
            return db_manager
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise MissionControllerError(f"Database initialization failed: {e}")
    
    def _initialize_auth(self) -> AuthManager:
        """Initialize authentication manager"""
        try:
            auth_manager = AuthManager(self.db)
            logger.info("Mission Control authentication initialized")
            return auth_manager
        except Exception as e:
            logger.error(f"Failed to initialize authentication: {e}")
            raise MissionControllerError(f"Authentication initialization failed: {e}")
    
    def _initialize_service(self) -> MissionService:
        """Initialize mission service"""
        try:
            service = MissionService(self.config, self.db, self.auth)
            logger.info("Mission Control service initialized")
            return service
        except Exception as e:
            logger.error(f"Failed to initialize service: {e}")
            raise MissionControllerError(f"Service initialization failed: {e}")
    
    def _setup_controller(self) -> None:
        """Setup controller components"""
        try:
            self.engine.register_module("mission_control_controller", self)
            logger.info("Mission Controller registered with core engine")
        except Exception as e:
            logger.error(f"Failed to register controller: {e}")
    
    def create_mission(self, context: MissionContext, mission_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new mission.
        
        Args:
            context: Mission context
            mission_config: Mission configuration
            
        Returns:
            Mission creation result
        """
        self._operation_count += 1
        return self.service.create_mission(context, mission_config)
    
    def get_mission_status(self, mission_id: str) -> Dict[str, Any]:
        """
        Get mission status.
        
        Args:
            mission_id: Mission identifier
            
        Returns:
            Mission status information
        """
        self._operation_count += 1
        return self.service.get_mission_status(mission_id)
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        Get system health status.
        
        Returns:
            System health information
        """
        self._operation_count += 1
        return self.service.get_system_health()
    
    def get_controller_metrics(self) -> Dict[str, Any]:
        """
        Get controller performance metrics.
        
        Returns:
            Controller metrics
        """
        uptime = (datetime.now() - self._start_time).total_seconds()
        return {
            "uptime_seconds": uptime,
            "operations_processed": self._operation_count,
            "active_missions": len(self.service._active_missions),
            "status": "running" if self.engine.status.value == "running" else "error"
        }
    
    def get_integration_status(self) -> Dict[str, Any]:
        """
        Get status of all integrations.
        
        Returns:
            Integration status dictionary
        """
        try:
            if self.integrations:
                return self.integrations.get_integration_status()
            return {"error": "Integrations not initialized"}
        except Exception as e:
            logger.error(f"Failed to get integration status: {e}")
            return {"error": str(e)}
    
    def get_aggregated_metrics(self) -> Dict[str, Any]:
        """
        Get aggregated metrics from all integrations.
        
        Returns:
            Aggregated metrics dictionary
        """
        try:
            if self.integrations and hasattr(self.integrations, 'metrics'):
                return self.integrations.metrics.aggregate_all_metrics()
            return {"error": "Metrics aggregator not initialized"}
        except Exception as e:
            logger.error(f"Failed to get aggregated metrics: {e}")
            return {"error": str(e)}
    
    def dispatch_alert(self, alert) -> bool:
        """
        Dispatch alert through integration channels.
        
        Args:
            alert: Alert to dispatch
            
        Returns:
            True if dispatched successfully, False otherwise
        """
        try:
            if self.integrations and hasattr(self.integrations, 'alerts'):
                return self.integrations.alerts.dispatch(alert)
            return False
        except Exception as e:
            logger.error(f"Failed to dispatch alert: {e}")
            return False
    
    def shutdown(self) -> None:
        """Shutdown mission controller"""
        try:
            logger.info("Shutting down Mission Controller...")
            if self.integrations:
                self.integrations.shutdown()
            if self.service:
                logger.info("Mission Control service shutdown complete")
            if self.db:
                self.db.close()
            logger.info("Mission Controller shutdown complete")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

