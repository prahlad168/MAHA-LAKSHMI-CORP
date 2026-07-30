#!/usr/bin/env python3
"""
MAHA Sales Engine V1 - Mission Control Product Factory Integration

Integrates Mission Control with the Product Factory module.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.logging_utils import get_logger
from mission_control.models import MissionContext, MissionMetric, MissionAlert

logger = get_logger("maha-sales-engine.mission-control.product-factory")


class ProductFactoryIntegration:
    """
    Integrates Mission Control with Product Factory.
    
    Provides visibility into product factory operations,
    tracks generation jobs, and monitors product metrics.
    """
    
    def __init__(self, mission_controller, product_factory=None):
        """
        Initialize product factory integration.
        
        Args:
            mission_controller: Mission controller instance
            product_factory: Optional product factory instance
        """
        self.mission_controller = mission_controller
        self.product_factory = product_factory
        self.logger = get_logger("maha-sales-engine.mission-control.product-factory")
    
    def get_factory_status(self) -> Dict[str, Any]:
        """
        Get product factory status.
        
        Returns:
            Factory status dictionary
        """
        try:
            if self.product_factory:
                status = self.product_factory.get_status()
                stats = self.product_factory.get_stats()
                return {
                    "status": "connected",
                    "factory_status": status,
                    "stats": stats,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "not_connected",
                    "message": "Product factory not initialized",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            self.logger.error(f"Failed to get factory status: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_generation_jobs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent product generation jobs.
        
        Args:
            limit: Maximum number of jobs to return
            
        Returns:
            List of generation jobs
        """
        try:
            if not self.product_factory:
                return []
            
            from product_factory.core.factory import GenerationJobStatus
            
            jobs = []
            # In production: query pf_generation_jobs table
            # For now, return empty list with structure
            return jobs
        except Exception as e:
            self.logger.error(f"Failed to get generation jobs: {e}")
            return []
    
    def track_product_metric(self, product_id: str, metric_name: str, value: float, unit: str = "count") -> bool:
        """
        Track product-related metric.
        
        Args:
            product_id: Product identifier
            metric_name: Metric name
            value: Metric value
            unit: Metric unit
            
        Returns:
            True if tracked successfully, False otherwise
        """
        try:
            metric = MissionMetric(
                metric_id=f"pf-{product_id}-{metric_name}-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                name=f"product_factory.{metric_name}",
                value=value,
                unit=unit,
                tags={"product_id": product_id}
            )
            
            from mission_control.repositories.mission_repository import MissionRepository
            repo = MissionRepository(self.mission_controller.db)
            return repo.record_metric(metric)
        except Exception as e:
            self.logger.error(f"Failed to track product metric: {e}")
            return False
    
    def create_product_alert(self, product_id: str, severity: str, message: str) -> bool:
        """
        Create alert for product factory event.
        
        Args:
            product_id: Product identifier
            severity: Alert severity (critical, warning, info)
            message: Alert message
            
        Returns:
            True if alert created successfully, False otherwise
        """
        try:
            alert = MissionAlert(
                alert_id=f"pf-{product_id}-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                severity=severity,
                message=message,
                source="product_factory",
                metadata={"product_id": product_id}
            )
            
            from mission_control.repositories.mission_repository import MissionRepository
            repo = MissionRepository(self.mission_controller.db)
            return repo.record_alert(alert)
        except Exception as e:
            self.logger.error(f"Failed to create product alert: {e}")
            return False
