"""
MAHA Sales Engine V1 - Mission Control Integrations

Integration layer connecting Mission Control with existing system modules.
"""

from .manager import IntegrationManager
from .event_bus import EventBus, Event, MissionControlEvents, event_bus
from .scheduler import SchedulerIntegration
from .health import HealthMonitoringIntegration, MissionControlHealthChecker
from .analytics import AnalyticsIntegration
from .product_factory import ProductFactoryIntegration
from .market_intelligence import MarketIntelligenceIntegration
from .sales_automation import SalesAutomationIntegration
from .metrics import MetricsAggregator
from .alerts import AlertDispatcher, AlertChannel
from .logging import LoggingIntegration, MissionControlLogger

__all__ = [
    "IntegrationManager",
    "EventBus",
    "Event",
    "MissionControlEvents",
    "event_bus",
    "SchedulerIntegration",
    "HealthMonitoringIntegration",
    "MissionControlHealthChecker",
    "AnalyticsIntegration",
    "ProductFactoryIntegration",
    "MarketIntelligenceIntegration",
    "SalesAutomationIntegration",
    "MetricsAggregator",
    "AlertDispatcher",
    "AlertChannel",
    "LoggingIntegration",
    "MissionControlLogger"
]
