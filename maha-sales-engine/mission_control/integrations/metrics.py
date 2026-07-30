#!/usr/bin/env python3
"""
MAHA Sales Engine V1 - Mission Control Metrics Aggregation

Aggregates metrics from all integrated systems.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.logging_utils import get_logger
from shared.monitoring import MetricsCollector
from mission_control.models import MissionMetric

logger = get_logger("maha-sales-engine.mission-control.metrics")


class MetricsAggregator:
    """
    Aggregates metrics from all Mission Control integrations.
    
    Provides unified metrics view across scheduler, health,
    analytics, product factory, market intelligence, and sales automation.
    """
    
    def __init__(self, mission_controller, metrics_collector: Optional[MetricsCollector] = None):
        """
        Initialize metrics aggregator.
        
        Args:
            mission_controller: Mission controller instance
            metrics_collector: Optional metrics collector instance
        """
        self.mission_controller = mission_controller
        self.collector = metrics_collector or MetricsCollector()
        self._metrics_cache: Dict[str, List[MissionMetric]] = {}
        self.logger = get_logger("maha-sales-engine.mission-control.metrics")
    
    def aggregate_all_metrics(self) -> Dict[str, Any]:
        """
        Aggregate metrics from all integrations.
        
        Returns:
            Aggregated metrics dictionary
        """
        try:
            aggregated = {
                "timestamp": datetime.now().isoformat(),
                "mission_control": self._get_mission_control_metrics(),
                "scheduler": self._get_scheduler_metrics(),
                "health": self._get_health_metrics(),
                "analytics": self._get_analytics_metrics(),
                "product_factory": self._get_product_factory_metrics(),
                "market_intelligence": self._get_market_intelligence_metrics(),
                "sales_automation": self._get_sales_automation_metrics()
            }
            
            # Record aggregated metrics
            self._record_aggregated_metrics(aggregated)
            
            return aggregated
        except Exception as e:
            self.logger.error(f"Failed to aggregate metrics: {e}")
            return {"error": str(e)}
    
    def _get_mission_control_metrics(self) -> Dict[str, Any]:
        """Get Mission Control metrics"""
        try:
            return self.mission_controller.get_controller_metrics()
        except Exception as e:
            self.logger.error(f"Failed to get mission control metrics: {e}")
            return {"error": str(e)}
    
    def _get_scheduler_metrics(self) -> Dict[str, Any]:
        """Get Scheduler metrics"""
        try:
            from mission_control.integrations.scheduler import SchedulerIntegration
            integration = SchedulerIntegration()
            jobs = integration.get_registered_jobs()
            return {
                "registered_jobs": len(jobs),
                "job_ids": list(jobs.keys())
            }
        except Exception as e:
            self.logger.error(f"Failed to get scheduler metrics: {e}")
            return {"error": str(e)}
    
    def _get_health_metrics(self) -> Dict[str, Any]:
        """Get Health metrics"""
        try:
            from mission_control.integrations.health import HealthMonitoringIntegration
            integration = HealthMonitoringIntegration(self.mission_controller)
            return integration.check_health()
        except Exception as e:
            self.logger.error(f"Failed to get health metrics: {e}")
            return {"error": str(e)}
    
    def _get_analytics_metrics(self) -> Dict[str, Any]:
        """Get Analytics metrics"""
        try:
            from mission_control.integrations.analytics import AnalyticsIntegration
            integration = AnalyticsIntegration(self.mission_controller)
            return integration.get_dashboard_data()
        except Exception as e:
            self.logger.error(f"Failed to get analytics metrics: {e}")
            return {"error": str(e)}
    
    def _get_product_factory_metrics(self) -> Dict[str, Any]:
        """Get Product Factory metrics"""
        try:
            from mission_control.integrations.product_factory import ProductFactoryIntegration
            integration = ProductFactoryIntegration(self.mission_controller)
            return integration.get_factory_status()
        except Exception as e:
            self.logger.error(f"Failed to get product factory metrics: {e}")
            return {"error": str(e)}
    
    def _get_market_intelligence_metrics(self) -> Dict[str, Any]:
        """Get Market Intelligence metrics"""
        try:
            from mission_control.integrations.market_intelligence import MarketIntelligenceIntegration
            integration = MarketIntelligenceIntegration(self.mission_controller)
            return integration.get_market_trends()
        except Exception as e:
            self.logger.error(f"Failed to get market intelligence metrics: {e}")
            return {"error": str(e)}
    
    def _get_sales_automation_metrics(self) -> Dict[str, Any]:
        """Get Sales Automation metrics"""
        try:
            from mission_control.integrations.sales_automation import SalesAutomationIntegration
            integration = SalesAutomationIntegration(self.mission_controller)
            return integration.get_automation_status()
        except Exception as e:
            self.logger.error(f"Failed to get sales automation metrics: {e}")
            return {"error": str(e)}
    
    def _record_aggregated_metrics(self, aggregated: Dict[str, Any]) -> None:
        """Record aggregated metrics to collector"""
        try:
            self.collector.gauge("mission_control.aggregated_metrics_count", len(aggregated))
            self.collector.gauge("mission_control.uptime_seconds", aggregated.get("mission_control", {}).get("uptime_seconds", 0))
            self.collector.gauge("mission_control.operations_processed", aggregated.get("mission_control", {}).get("operations_processed", 0))
        except Exception as e:
            self.logger.error(f"Failed to record aggregated metrics: {e}")
    
    def get_metrics_trend(self, metric_name: str, hours: int = 24) -> Dict[str, Any]:
        """
        Get metrics trend over time.
        
        Args:
            metric_name: Metric name
            hours: Number of hours to look back
            
        Returns:
            Metrics trend dictionary
        """
        try:
            # In production: query stored metrics from database
            # For now, return empty trend
            return {
                "metric_name": metric_name,
                "hours": hours,
                "data_points": [],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to get metrics trend: {e}")
            return {"error": str(e)}
    
    def get_prometheus_metrics(self) -> str:
        """
        Get metrics in Prometheus format.
        
        Returns:
            Prometheus formatted metrics string
        """
        try:
            return self.collector.prometheus.export()
        except Exception as e:
            self.logger.error(f"Failed to export Prometheus metrics: {e}")
            return ""
