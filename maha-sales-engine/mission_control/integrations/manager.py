#!/usr/bin/env python3
"""
MAHA Sales Engine V1 - Mission Control Integration Manager

Central manager for all Mission Control integrations.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.logging_utils import get_logger
from mission_control.models import MissionContext

logger = get_logger("maha-sales-engine.mission-control.integrations")


class IntegrationManager:
    """
    Central manager for Mission Control integrations.
    
    Coordinates all integration modules and provides
    unified access to external system capabilities.
    """
    
    def __init__(self, mission_controller):
        """
        Initialize integration manager.
        
        Args:
            mission_controller: Mission controller instance
        """
        self.mission_controller = mission_controller
        self._integrations: Dict[str, Any] = {}
        self.logger = get_logger("maha-sales-engine.mission-control.integrations")
        self._setup_integrations()
    
    def _setup_integrations(self) -> None:
        """Setup all integrations"""
        try:
            # Event Bus
            from mission_control.integrations.event_bus import EventBus, MissionControlEvents
            self.event_bus = EventBus()
            self.event_types = MissionControlEvents
            self._integrations["event_bus"] = self.event_bus
            self._setup_event_handlers()
            
            # Scheduler
            from mission_control.integrations.scheduler import SchedulerIntegration
            self.scheduler = SchedulerIntegration()
            self._integrations["scheduler"] = self.scheduler
            
            # Health Monitoring
            from mission_control.integrations.health import HealthMonitoringIntegration
            self.health = HealthMonitoringIntegration(self.mission_controller)
            self._integrations["health"] = self.health
            
            # Analytics
            from mission_control.integrations.analytics import AnalyticsIntegration
            self.analytics = AnalyticsIntegration(self.mission_controller)
            self._integrations["analytics"] = self.analytics
            
            # Product Factory
            from mission_control.integrations.product_factory import ProductFactoryIntegration
            self.product_factory = ProductFactoryIntegration(self.mission_controller)
            self._integrations["product_factory"] = self.product_factory
            
            # Market Intelligence
            from mission_control.integrations.market_intelligence import MarketIntelligenceIntegration
            self.market_intelligence = MarketIntelligenceIntegration(self.mission_controller)
            self._integrations["market_intelligence"] = self.market_intelligence
            
            # Sales Automation
            from mission_control.integrations.sales_automation import SalesAutomationIntegration
            self.sales_automation = SalesAutomationIntegration(self.mission_controller)
            self._integrations["sales_automation"] = self.sales_automation
            
            # Metrics Aggregator
            from mission_control.integrations.metrics import MetricsAggregator
            from shared.monitoring import MetricsCollector
            self.metrics = MetricsAggregator(self.mission_controller)
            self._integrations["metrics"] = self.metrics
            
            # Alert Dispatcher
            from mission_control.integrations.alerts import AlertDispatcher
            self.alerts = AlertDispatcher()
            self._integrations["alerts"] = self.alerts
            
            # Logging
            from mission_control.integrations.logging import LoggingIntegration
            self.logging = LoggingIntegration(self.mission_controller)
            self._integrations["logging"] = self.logging
            
            logger.info("All Mission Control integrations initialized")
        except Exception as e:
            logger.error(f"Failed to setup integrations: {e}")
            raise
    
    def _setup_event_handlers(self) -> None:
        """Setup default event handlers"""
        try:
            self.event_bus.subscribe(self.event_types.MISSION_CREATED, self._on_mission_created)
            self.event_bus.subscribe(self.event_types.MISSION_STARTED, self._on_mission_started)
            self.event_bus.subscribe(self.event_types.MISSION_COMPLETED, self._on_mission_completed)
            self.event_bus.subscribe(self.event_types.MISSION_FAILED, self._on_mission_failed)
            self.event_bus.subscribe(self.event_types.ALERT_CREATED, self._on_alert_created)
            logger.info("Event handlers registered")
        except Exception as e:
            logger.error(f"Failed to setup event handlers: {e}")
    
    def _on_mission_created(self, event) -> None:
        """Handle mission created event"""
        self.logger.info(f"Mission created: {event.data.get('mission_id')}")
    
    def _on_mission_started(self, event) -> None:
        """Handle mission started event"""
        self.logger.info(f"Mission started: {event.data.get('mission_id')}")
    
    def _on_mission_completed(self, event) -> None:
        """Handle mission completed event"""
        self.logger.info(f"Mission completed: {event.data.get('mission_id')}")
    
    def _on_mission_failed(self, event) -> None:
        """Handle mission failed event"""
        self.logger.error(f"Mission failed: {event.data.get('mission_id')}")
    
    def _on_alert_created(self, event) -> None:
        """Handle alert created event"""
        alert_data = event.data
        self.logger.warning(f"Alert created: {alert_data.get('severity')}: {alert_data.get('message')}")
    
    def get_integration(self, name: str) -> Optional[Any]:
        """
        Get integration by name.
        
        Args:
            name: Integration name
            
        Returns:
            Integration instance or None
        """
        return self._integrations.get(name)
    
    def get_all_integrations(self) -> Dict[str, Any]:
        """
        Get all integrations.
        
        Returns:
            Dictionary of integration names to instances
        """
        return dict(self._integrations)
    
    def get_integration_status(self) -> Dict[str, Any]:
        """
        Get status of all integrations.
        
        Returns:
            Integration status dictionary
        """
        status = {}
        for name, integration in self._integrations.items():
            try:
                if hasattr(integration, 'get_status'):
                    status[name] = integration.get_status()
                elif hasattr(integration, 'check_health'):
                    status[name] = integration.check_health()
                else:
                    status[name] = {"status": "active", "type": type(integration).__name__}
            except Exception as e:
                status[name] = {"status": "error", "error": str(e)}
        
        return {
            "integrations": status,
            "total": len(status),
            "timestamp": datetime.now().isoformat()
        }
    
    def publish_event(self, event_type: str, data: Dict[str, Any], source: str = "mission-control") -> bool:
        """
        Publish event to event bus.
        
        Args:
            event_type: Event type
            data: Event data
            source: Event source
            
        Returns:
            True if published successfully, False otherwise
        """
        try:
            from mission_control.integrations.event_bus import Event
            event = Event(event_type, data, source)
            return self.event_bus.publish(event)
        except Exception as e:
            self.logger.error(f"Failed to publish event: {e}")
            return False
    
    def get_aggregated_metrics(self) -> Dict[str, Any]:
        """
        Get aggregated metrics from all integrations.
        
        Returns:
            Aggregated metrics dictionary
        """
        try:
            if hasattr(self, 'metrics'):
                return self.metrics.aggregate_all_metrics()
            return {"error": "Metrics aggregator not initialized"}
        except Exception as e:
            self.logger.error(f"Failed to get aggregated metrics: {e}")
            return {"error": str(e)}
    
    def shutdown(self) -> None:
        """Shutdown all integrations"""
        try:
            if hasattr(self, 'scheduler'):
                self.scheduler.unregister_all_jobs()
            logger.info("Integration manager shutdown complete")
        except Exception as e:
            logger.error(f"Error during integration shutdown: {e}")
