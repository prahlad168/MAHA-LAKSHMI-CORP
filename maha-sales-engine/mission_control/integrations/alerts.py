#!/usr/bin/env python3
"""
MAHA Sales Engine V1 - Mission Control Alert Dispatcher

Dispatches alerts through multiple channels.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.logging_utils import get_logger
from mission_control.models import MissionAlert

logger = get_logger("maha-sales-engine.mission-control.alerts")


class AlertChannel(Enum):
    """Alert dispatch channels"""
    LOG = "log"
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    DATABASE = "database"


class AlertDispatcher:
    """
    Dispatches alerts through multiple channels.
    
    Supports log, email, slack, webhook, and database channels.
    """
    
    def __init__(self):
        self._channels: Dict[str, List[callable]] = {
            AlertChannel.LOG.value: [self._log_alert],
            AlertChannel.DATABASE.value: [self._store_alert]
        }
        self.logger = get_logger("maha-sales-engine.mission-control.alerts")
    
    def register_channel(self, channel: AlertChannel, handler: callable) -> None:
        """
        Register alert handler for channel.
        
        Args:
            channel: Alert channel
            handler: Handler function
        """
        self._channels[channel.value].append(handler)
        self.logger.info(f"Registered alert handler for channel: {channel.value}")
    
    def dispatch(self, alert: MissionAlert) -> bool:
        """
        Dispatch alert to all registered channels.
        
        Args:
            alert: Alert to dispatch
            
        Returns:
            True if dispatched successfully, False otherwise
        """
        try:
            success = True
            for channel_name, handlers in self._channels.items():
                for handler in handlers:
                    try:
                        result = handler(alert)
                        if not result:
                            success = False
                    except Exception as e:
                        self.logger.error(f"Alert handler failed for {channel_name}: {e}")
                        success = False
            
            return success
        except Exception as e:
            self.logger.error(f"Failed to dispatch alert {alert.alert_id}: {e}")
            return False
    
    def _log_alert(self, alert: MissionAlert) -> bool:
        """Log alert to structured logger"""
        try:
            log_method = {
                "critical": self.logger.critical,
                "warning": self.logger.warning,
                "info": self.logger.info
            }.get(alert.severity, self.logger.info)
            
            log_method(
                f"ALERT [{alert.severity.upper()}]: {alert.message}",
                alert_id=alert.alert_id,
                source=alert.source,
                metadata=alert.metadata
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to log alert: {e}")
            return False
    
    def _store_alert(self, alert: MissionAlert) -> bool:
        """Store alert in database"""
        try:
            from mission_control.repositories.mission_repository import MissionRepository
            # This would need a database manager instance
            # For now, just return True
            return True
        except Exception as e:
            self.logger.error(f"Failed to store alert: {e}")
            return False
    
    def dispatch_email(self, alert: MissionAlert, recipient: str) -> bool:
        """
        Dispatch alert via email.
        
        Args:
            alert: Alert to dispatch
            recipient: Email recipient
            
        Returns:
            True if dispatched successfully, False otherwise
        """
        try:
            # In production: integrate with email provider
            self.logger.info(f"Dispatching alert via email to {recipient}: {alert.message}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to dispatch email alert: {e}")
            return False
    
    def dispatch_slack(self, alert: MissionAlert, channel: str = "#alerts") -> bool:
        """
        Dispatch alert via Slack.
        
        Args:
            alert: Alert to dispatch
            channel: Slack channel
            
        Returns:
            True if dispatched successfully, False otherwise
        """
        try:
            # In production: integrate with Slack API
            self.logger.info(f"Dispatching alert via Slack to {channel}: {alert.message}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to dispatch Slack alert: {e}")
            return False
    
    def dispatch_webhook(self, alert: MissionAlert, webhook_url: str) -> bool:
        """
        Dispatch alert via webhook.
        
        Args:
            alert: Alert to dispatch
            webhook_url: Webhook URL
            
        Returns:
            True if dispatched successfully, False otherwise
        """
        try:
            # In production: send HTTP POST to webhook
            self.logger.info(f"Dispatching alert via webhook to {webhook_url}: {alert.message}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to dispatch webhook alert: {e}")
            return False
