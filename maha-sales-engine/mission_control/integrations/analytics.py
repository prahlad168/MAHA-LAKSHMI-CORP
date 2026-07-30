#!/usr/bin/env python3
"""
MAHA Sales Engine V1 - Mission Control Analytics Integration

Integrates Mission Control with the existing Analytics module.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.logging_utils import get_logger
from mission_control.models import MissionContext, MissionMetric

logger = get_logger("maha-sales-engine.mission-control.analytics")


class AnalyticsIntegration:
    """
    Integrates Mission Control with the Analytics module.
    
    Provides mission-aware analytics by combining mission control
    data with existing analytics data.
    """
    
    def __init__(self, mission_controller, analytics_engine=None):
        """
        Initialize analytics integration.
        
        Args:
            mission_controller: Mission controller instance
            analytics_engine: Optional analytics engine instance
        """
        self.mission_controller = mission_controller
        self.analytics = analytics_engine
        self.logger = get_logger("maha-sales-engine.mission-control.analytics")
    
    def get_mission_analytics(self, mission_id: str, days: int = 7) -> Dict[str, Any]:
        """
        Get analytics for a specific mission.
        
        Args:
            mission_id: Mission identifier
            days: Number of days to analyze
            
        Returns:
            Mission analytics dictionary
        """
        try:
            from mission_control.repositories.mission_repository import MissionRepository
            repo = MissionRepository(self.mission_controller.db)
            
            mission = repo.get_mission(mission_id)
            if not mission:
                return {"error": f"Mission {mission_id} not found"}
            
            # Get mission metrics
            metrics = repo.get_mission_metrics(mission_id, limit=1000)
            
            # Aggregate metrics
            aggregated = self._aggregate_metrics(metrics)
            
            # Get existing analytics if available
            system_analytics = {}
            if self.analytics:
                try:
                    system_analytics = self.analytics.get_dashboard_summary()
                except Exception as e:
                    self.logger.warning(f"Failed to get system analytics: {e}")
            
            return {
                "mission_id": mission_id,
                "mission_name": mission.name,
                "status": mission.status,
                "period_days": days,
                "metrics": aggregated,
                "system_analytics": system_analytics,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to get mission analytics: {e}")
            return {"error": str(e)}
    
    def _aggregate_metrics(self, metrics: List[Any]) -> Dict[str, Any]:
        """
        Aggregate mission metrics.
        
        Args:
            metrics: List of mission metrics
            
        Returns:
            Aggregated metrics dictionary
        """
        try:
            from mission_control.models import MissionMetric
            
            aggregated = {
                "total_metrics": len(metrics),
                "by_name": {},
                "by_unit": {},
                "time_series": []
            }
            
            for metric in metrics:
                if isinstance(metric, dict):
                    name = metric.get("name", "unknown")
                    value = metric.get("value", 0)
                    unit = metric.get("unit", "")
                    timestamp = metric.get("timestamp", "")
                else:
                    name = metric.name
                    value = metric.value
                    unit = metric.unit
                    timestamp = metric.timestamp
                
                if name not in aggregated["by_name"]:
                    aggregated["by_name"][name] = []
                aggregated["by_name"][name].append(value)
                
                if unit not in aggregated["by_unit"]:
                    aggregated["by_unit"][unit] = []
                aggregated["by_unit"][unit].append(value)
                
                aggregated["time_series"].append({
                    "name": name,
                    "value": value,
                    "unit": unit,
                    "timestamp": timestamp
                })
            
            # Calculate statistics
            for name, values in aggregated["by_name"].items():
                if values:
                    aggregated["by_name"][name] = {
                        "count": len(values),
                        "sum": sum(values),
                        "avg": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values)
                    }
            
            return aggregated
        except Exception as e:
            self.logger.error(f"Failed to aggregate metrics: {e}")
            return {"error": str(e)}
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get combined dashboard data for Mission Control.
        
        Returns:
            Dashboard data dictionary
        """
        try:
            # Get mission control data
            controller_metrics = self.mission_controller.get_controller_metrics()
            system_health = self.mission_controller.get_system_health()
            
            # Get analytics data if available
            analytics_data = {}
            if self.analytics:
                try:
                    analytics_data = self.analytics.get_dashboard_summary()
                except Exception as e:
                    self.logger.warning(f"Failed to get analytics dashboard: {e}")
            
            return {
                "mission_control": {
                    "metrics": controller_metrics,
                    "health": system_health
                },
                "analytics": analytics_data,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to get dashboard data: {e}")
            return {"error": str(e)}
