#!/usr/bin/env python3
"""
MAHA Sales Engine V1 - Mission Control Sales Automation Integration

Integrates Mission Control with the Sales Automation module.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.logging_utils import get_logger
from mission_control.models import MissionContext, MissionMetric, MissionAlert

logger = get_logger("maha-sales-engine.mission-control.sales-automation")


class SalesAutomationIntegration:
    """
    Integrates Mission Control with Sales Automation.
    
    Provides visibility into sales automation operations,
    tracks campaign performance, and monitors automation health.
    """
    
    def __init__(self, mission_controller, sales_automation_core=None):
        """
        Initialize sales automation integration.
        
        Args:
            mission_controller: Mission controller instance
            sales_automation_core: Optional sales automation core instance
        """
        self.mission_controller = mission_controller
        self.sales_core = sales_automation_core
        self.logger = get_logger("maha-sales-engine.mission-control.sales-automation")
    
    def get_automation_status(self) -> Dict[str, Any]:
        """
        Get sales automation status.
        
        Returns:
            Automation status dictionary
        """
        try:
            if self.sales_core:
                status = self.sales_core.get_status()
                return {
                    "status": "connected",
                    "automation_status": status,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "not_connected",
                    "message": "Sales automation not initialized",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            self.logger.error(f"Failed to get automation status: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_campaign_metrics(self) -> Dict[str, Any]:
        """
        Get sales campaign metrics.
        
        Returns:
            Campaign metrics dictionary
        """
        try:
            if self.sales_core and hasattr(self.sales_core, 'campaign_engine'):
                # In production: query campaign metrics
                return {
                    "status": "success",
                    "campaigns": [],
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "not_available",
                    "message": "Campaign engine not available",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            self.logger.error(f"Failed to get campaign metrics: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """
        Get automation queue statistics.
        
        Returns:
            Queue statistics dictionary
        """
        try:
            if self.sales_core and hasattr(self.sales_core, 'queue_engine'):
                stats = self.sales_core.queue_engine.get_stats()
                return {
                    "status": "success",
                    "queue_stats": stats,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "not_available",
                    "message": "Queue engine not available",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            self.logger.error(f"Failed to get queue stats: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """
        Get workflow engine status.
        
        Returns:
            Workflow status dictionary
        """
        try:
            if self.sales_core and hasattr(self.sales_core, 'workflow_engine'):
                # In production: get workflow status
                return {
                    "status": "success",
                    "workflows": [],
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "not_available",
                    "message": "Workflow engine not available",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            self.logger.error(f"Failed to get workflow status: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def track_sales_metric(self, metric_name: str, value: float, unit: str = "count", tags: Dict[str, str] = None) -> bool:
        """
        Track sales automation metric.
        
        Args:
            metric_name: Metric name
            value: Metric value
            unit: Metric unit
            tags: Optional tags
            
        Returns:
            True if tracked successfully, False otherwise
        """
        try:
            metric = MissionMetric(
                metric_id=f"sa-{metric_name}-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                name=f"sales_automation.{metric_name}",
                value=value,
                unit=unit,
                tags=tags or {}
            )
            
            from mission_control.repositories.mission_repository import MissionRepository
            repo = MissionRepository(self.mission_controller.db)
            return repo.record_metric(metric)
        except Exception as e:
            self.logger.error(f"Failed to track sales metric: {e}")
            return False
