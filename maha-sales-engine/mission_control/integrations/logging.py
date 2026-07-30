#!/usr/bin/env python3
"""
MAHA Sales Engine V1 - Mission Control Structured Logging Integration

Integrates Mission Control with the shared Structured Logging system.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from functools import wraps

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.logging_utils import get_logger, StructuredLogger, LoggingManager

logger = get_logger("maha-sales-engine.mission-control.logging")


class MissionControlLogger:
    """
    Mission Control structured logging integration.
    
    Provides structured logging with mission context correlation.
    """
    
    def __init__(self, name: str = "mission-control"):
        """
        Initialize mission control logger.
        
        Args:
            name: Logger name
        """
        self.logger = get_logger(f"maha-sales-engine.{name}")
        self._request_id: Optional[str] = None
        self._mission_id: Optional[str] = None
    
    def set_mission_context(self, mission_id: str, request_id: Optional[str] = None) -> None:
        """
        Set mission context for logging.
        
        Args:
            mission_id: Mission identifier
            request_id: Optional request identifier
        """
        self._mission_id = mission_id
        self._request_id = request_id
    
    def clear_context(self) -> None:
        """Clear mission context"""
        self._mission_id = None
        self._request_id = None
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message with mission context"""
        extra = self._build_extra(kwargs)
        self.logger.info(message, extra={"extra": extra})
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message with mission context"""
        extra = self._build_extra(kwargs)
        self.logger.debug(message, extra={"extra": extra})
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message with mission context"""
        extra = self._build_extra(kwargs)
        self.logger.warning(message, extra={"extra": extra})
    
    def error(self, message: str, error: Optional[Exception] = None, **kwargs) -> None:
        """Log error message with mission context"""
        extra = self._build_extra(kwargs)
        if error:
            extra["error_type"] = type(error).__name__
            extra["error_message"] = str(error)
            extra["traceback"] = self._get_traceback()
        self.logger.error(message, extra={"extra": extra})
    
    def critical(self, message: str, error: Optional[Exception] = None, **kwargs) -> None:
        """Log critical message with mission context"""
        extra = self._build_extra(kwargs)
        if error:
            extra["error_type"] = type(error).__name__
            extra["error_message"] = str(error)
            extra["traceback"] = self._get_traceback()
        self.logger.critical(message, extra={"extra": extra})
    
    def _build_extra(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Build extra context for logging"""
        extra = {
            "request_id": self._request_id,
            "mission_id": self._mission_id,
            "timestamp": datetime.now().isoformat()
        }
        extra.update(kwargs)
        return extra
    
    def _get_traceback(self) -> Optional[str]:
        """Get current traceback"""
        import traceback
        return traceback.format_exc()


class LoggingIntegration:
    """
    Integrates Mission Control with the shared Logging system.
    
    Provides centralized logging configuration and
    mission-aware log correlation.
    """
    
    def __init__(self, mission_controller):
        """
        Initialize logging integration.
        
        Args:
            mission_controller: Mission controller instance
        """
        self.mission_controller = mission_controller
        self.logger = get_logger("maha-sales-engine.mission-control.logging")
        self._logging_manager = LoggingManager()
    
    def setup_logging(self, config: Dict[str, Any]) -> None:
        """
        Setup logging from configuration.
        
        Args:
            config: Logging configuration dictionary
        """
        try:
            self._logging_manager.setup(config)
            self.logger.info("Mission Control logging configured")
        except Exception as e:
            self.logger.error(f"Failed to setup logging: {e}")
    
    def get_logger(self, name: str) -> MissionControlLogger:
        """
        Get Mission Control logger instance.
        
        Args:
            name: Logger name
            
        Returns:
            MissionControlLogger instance
        """
        return MissionControlLogger(name)
    
    def log_mission_event(self, mission_id: str, event_type: str, message: str, **kwargs) -> None:
        """
        Log mission-specific event.
        
        Args:
            mission_id: Mission identifier
            event_type: Event type
            message: Log message
            **kwargs: Additional context
        """
        try:
            mission_logger = self.get_logger("mission-control.events")
            mission_logger.set_mission_context(mission_id)
            mission_logger.info(f"[{event_type}] {message}", **kwargs)
            mission_logger.clear_context()
        except Exception as e:
            self.logger.error(f"Failed to log mission event: {e}")
    
    def log_integration_event(self, integration_name: str, event_type: str, message: str, **kwargs) -> None:
        """
        Log integration-specific event.
        
        Args:
            integration_name: Integration name
            event_type: Event type
            message: Log message
            **kwargs: Additional context
        """
        try:
            integration_logger = self.get_logger(f"mission-control.integrations.{integration_name}")
            integration_logger.info(f"[{event_type}] {message}", **kwargs)
        except Exception as e:
            self.logger.error(f"Failed to log integration event: {e}")
