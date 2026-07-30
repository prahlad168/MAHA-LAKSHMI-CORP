#!/usr/bin/env python3
"""
MAHA Sales Engine V1 - Mission Control Integration Tests

Test suite for Mission Control integrations.
"""

import sys
import os
import pytest
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.database import DatabaseManager
from shared.auth import AuthManager
from mission_control.models import MissionContext, MissionConfig, MissionStatus, PermissionLevel, MissionMetric, MissionAlert
from mission_control.core.mission_controller import MissionController
from mission_control.integrations.manager import IntegrationManager
from mission_control.integrations.event_bus import EventBus, Event, MissionControlEvents
from mission_control.integrations.scheduler import SchedulerIntegration
from mission_control.integrations.health import HealthMonitoringIntegration, MissionControlHealthChecker
from mission_control.integrations.analytics import AnalyticsIntegration
from mission_control.integrations.product_factory import ProductFactoryIntegration
from mission_control.integrations.market_intelligence import MarketIntelligenceIntegration
from mission_control.integrations.sales_automation import SalesAutomationIntegration
from mission_control.integrations.metrics import MetricsAggregator
from mission_control.integrations.alerts import AlertDispatcher, AlertChannel
from mission_control.integrations.logging import LoggingIntegration, MissionControlLogger


@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    import tempfile
    db_path = tempfile.mktemp(suffix=".db")
    db_manager = DatabaseManager(db_path)
    yield db_manager
    db_manager.close()
    try:
        os.unlink(db_path)
    except FileNotFoundError:
        pass


@pytest.fixture
def mission_controller():
    """Create mission controller for testing"""
    controller = MissionController()
    yield controller


class TestEventBus:
    """Test EventBus"""
    
    def test_event_creation(self):
        """Test event creation"""
        event = Event("test.event", {"key": "value"}, "test")
        assert event.event_type == "test.event"
        assert event.data == {"key": "value"}
        assert event.source == "test"
        assert event.event_id is not None
    
    def test_event_to_dict(self):
        """Test event serialization"""
        event = Event("test.event", {"key": "value"}, "test")
        event_dict = event.to_dict()
        assert event_dict["event_type"] == "test.event"
        assert event_dict["data"] == {"key": "value"}
    
    def test_subscribe_and_publish(self):
        """Test subscribe and publish"""
        bus = EventBus()
        received_events = []
        
        def handler(event):
            received_events.append(event)
        
        bus.subscribe("test.event", handler)
        event = Event("test.event", {"key": "value"})
        result = bus.publish(event)
        
        assert result is True
        assert len(received_events) == 1
        assert received_events[0].event_type == "test.event"
    
    def test_unsubscribe(self):
        """Test unsubscribe"""
        bus = EventBus()
        received_events = []
        
        def handler(event):
            received_events.append(event)
        
        bus.subscribe("test.event", handler)
        bus.unsubscribe("test.event", handler)
        event = Event("test.event", {"key": "value"})
        bus.publish(event)
        
        assert len(received_events) == 0
    
    def test_event_history(self):
        """Test event history"""
        bus = EventBus()
        event1 = Event("test.event1", {"key": "value1"})
        event2 = Event("test.event2", {"key": "value2"})
        bus.publish(event1)
        bus.publish(event2)
        
        history = bus.get_history(limit=10)
        assert len(history) == 2
        assert history[0]["event_type"] == "test.event1"


class TestSchedulerIntegration:
    """Test SchedulerIntegration"""
    
    def test_initialization(self):
        """Test scheduler integration initialization"""
        integration = SchedulerIntegration()
        assert integration.scheduler is None
        assert integration.get_registered_jobs() == {}


class TestHealthMonitoringIntegration:
    """Test HealthMonitoringIntegration"""
    
    def test_initialization(self, mission_controller):
        """Test health monitoring integration initialization"""
        integration = HealthMonitoringIntegration(mission_controller)
        assert integration.mission_controller is mission_controller
    
    def test_check_health(self, mission_controller):
        """Test health check"""
        integration = HealthMonitoringIntegration(mission_controller)
        health = integration.check_health()
        assert "component" in health
        assert "status" in health
        assert health["component"] == "mission_control"


class TestAnalyticsIntegration:
    """Test AnalyticsIntegration"""
    
    def test_initialization(self, mission_controller):
        """Test analytics integration initialization"""
        integration = AnalyticsIntegration(mission_controller)
        assert integration.mission_controller is mission_controller
    
    def test_get_dashboard_data(self, mission_controller):
        """Test dashboard data retrieval"""
        integration = AnalyticsIntegration(mission_controller)
        data = integration.get_dashboard_data()
        assert "mission_control" in data
        assert "timestamp" in data


class TestProductFactoryIntegration:
    """Test ProductFactoryIntegration"""
    
    def test_initialization(self, mission_controller):
        """Test product factory integration initialization"""
        integration = ProductFactoryIntegration(mission_controller)
        assert integration.mission_controller is mission_controller
    
    def test_get_factory_status_not_connected(self, mission_controller):
        """Test factory status when not connected"""
        integration = ProductFactoryIntegration(mission_controller)
        status = integration.get_factory_status()
        assert status["status"] == "not_connected"


class TestMarketIntelligenceIntegration:
    """Test MarketIntelligenceIntegration"""
    
    def test_initialization(self, mission_controller):
        """Test market intelligence integration initialization"""
        integration = MarketIntelligenceIntegration(mission_controller)
        assert integration.mission_controller is mission_controller
    
    def test_get_market_trends_not_connected(self, mission_controller):
        """Test market trends when not connected"""
        integration = MarketIntelligenceIntegration(mission_controller)
        trends = integration.get_market_trends()
        assert trends["status"] == "not_connected"


class TestSalesAutomationIntegration:
    """Test SalesAutomationIntegration"""
    
    def test_initialization(self, mission_controller):
        """Test sales automation integration initialization"""
        integration = SalesAutomationIntegration(mission_controller)
        assert integration.mission_controller is mission_controller
    
    def test_get_automation_status_not_connected(self, mission_controller):
        """Test automation status when not connected"""
        integration = SalesAutomationIntegration(mission_controller)
        status = integration.get_automation_status()
        assert status["status"] == "not_connected"


class TestMetricsAggregator:
    """Test MetricsAggregator"""
    
    def test_initialization(self, mission_controller):
        """Test metrics aggregator initialization"""
        aggregator = MetricsAggregator(mission_controller)
        assert aggregator.mission_controller is mission_controller
    
    def test_aggregate_all_metrics(self, mission_controller):
        """Test metrics aggregation"""
        aggregator = MetricsAggregator(mission_controller)
        metrics = aggregator.aggregate_all_metrics()
        assert "timestamp" in metrics
        assert "mission_control" in metrics


class TestAlertDispatcher:
    """Test AlertDispatcher"""
    
    def test_initialization(self):
        """Test alert dispatcher initialization"""
        dispatcher = AlertDispatcher()
        assert AlertChannel.LOG.value in dispatcher._channels
    
    def test_dispatch_alert(self):
        """Test alert dispatch"""
        dispatcher = AlertDispatcher()
        alert = MissionAlert(
            alert_id="test-alert-001",
            severity="warning",
            message="Test alert",
            source="test"
        )
        result = dispatcher.dispatch(alert)
        assert result is True
    
    def test_dispatch_email(self):
        """Test email dispatch"""
        dispatcher = AlertDispatcher()
        alert = MissionAlert(
            alert_id="test-alert-002",
            severity="info",
            message="Test email alert",
            source="test"
        )
        result = dispatcher.dispatch_email(alert, "test@example.com")
        assert result is True
    
    def test_dispatch_slack(self):
        """Test Slack dispatch"""
        dispatcher = AlertDispatcher()
        alert = MissionAlert(
            alert_id="test-alert-003",
            severity="critical",
            message="Test Slack alert",
            source="test"
        )
        result = dispatcher.dispatch_slack(alert, "#alerts")
        assert result is True
    
    def test_dispatch_webhook(self):
        """Test webhook dispatch"""
        dispatcher = AlertDispatcher()
        alert = MissionAlert(
            alert_id="test-alert-004",
            severity="warning",
            message="Test webhook alert",
            source="test"
        )
        result = dispatcher.dispatch_webhook(alert, "https://example.com/webhook")
        assert result is True


class TestLoggingIntegration:
    """Test LoggingIntegration"""
    
    def test_initialization(self, mission_controller):
        """Test logging integration initialization"""
        integration = LoggingIntegration(mission_controller)
        assert integration.mission_controller is mission_controller
    
    def test_get_logger(self, mission_controller):
        """Test getting logger"""
        integration = LoggingIntegration(mission_controller)
        mc_logger = integration.get_logger("test")
        assert isinstance(mc_logger, MissionControlLogger)
    
    def test_mission_context_logging(self, mission_controller):
        """Test mission context logging"""
        integration = LoggingIntegration(mission_controller)
        mc_logger = integration.get_logger("test")
        mc_logger.set_mission_context("test-mission-001")
        mc_logger.info("Test message")
        mc_logger.clear_context()


class TestIntegrationManager:
    """Test IntegrationManager"""
    
    def test_initialization(self, mission_controller):
        """Test integration manager initialization"""
        manager = IntegrationManager(mission_controller)
        assert manager.mission_controller is mission_controller
        assert "event_bus" in manager.get_all_integrations()
        assert "scheduler" in manager.get_all_integrations()
        assert "health" in manager.get_all_integrations()
        assert "analytics" in manager.get_all_integrations()
        assert "product_factory" in manager.get_all_integrations()
        assert "market_intelligence" in manager.get_all_integrations()
        assert "sales_automation" in manager.get_all_integrations()
        assert "metrics" in manager.get_all_integrations()
        assert "alerts" in manager.get_all_integrations()
        assert "logging" in manager.get_all_integrations()
    
    def test_get_integration(self, mission_controller):
        """Test getting integration by name"""
        manager = IntegrationManager(mission_controller)
        event_bus = manager.get_integration("event_bus")
        assert event_bus is not None
        assert isinstance(event_bus, EventBus)
    
    def test_get_integration_status(self, mission_controller):
        """Test getting integration status"""
        manager = IntegrationManager(mission_controller)
        status = manager.get_integration_status()
        assert "integrations" in status
        assert "total" in status
        assert status["total"] == 10
    
    def test_publish_event(self, mission_controller):
        """Test event publishing"""
        manager = IntegrationManager(mission_controller)
        result = manager.publish_event("test.event", {"key": "value"})
        assert result is True
    
    def test_get_aggregated_metrics(self, mission_controller):
        """Test aggregated metrics"""
        manager = IntegrationManager(mission_controller)
        metrics = manager.get_aggregated_metrics()
        assert "timestamp" in metrics
        assert "mission_control" in metrics


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
