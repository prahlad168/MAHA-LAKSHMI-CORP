#!/usr/bin/env python3
"""
MAHA Sales Engine V1 - Mission Control Market Intelligence Integration

Integrates Mission Control with the Market Intelligence module.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.logging_utils import get_logger
from mission_control.models import MissionContext, MissionMetric

logger = get_logger("maha-sales-engine.mission-control.market-intelligence")


class MarketIntelligenceIntegration:
    """
    Integrates Mission Control with Market Intelligence.
    
    Provides market insights and opportunity scoring
    integrated with mission control operations.
    """
    
    def __init__(self, mission_controller, market_intelligence=None):
        """
        Initialize market intelligence integration.
        
        Args:
            mission_controller: Mission controller instance
            market_intelligence: Optional market intelligence instance
        """
        self.mission_controller = mission_controller
        self.market_intel = market_intelligence
        self.logger = get_logger("maha-sales-engine.mission-control.market-intelligence")
    
    def get_market_trends(self) -> Dict[str, Any]:
        """
        Get current market trends.
        
        Returns:
            Market trends dictionary
        """
        try:
            if self.market_intel:
                trends = self.market_intel.analyze_digital_product_trends()
                return {
                    "status": "success",
                    "trends": trends,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "not_connected",
                    "message": "Market intelligence not initialized",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            self.logger.error(f"Failed to get market trends: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_opportunity_score(self, country: str, product: str) -> Dict[str, Any]:
        """
        Get market opportunity score.
        
        Args:
            country: Country name
            product: Product identifier
            
        Returns:
            Opportunity score dictionary
        """
        try:
            if self.market_intel:
                score = self.market_intel.score_opportunity(country, product)
                return {
                    "status": "success",
                    "country": country,
                    "product": product,
                    "opportunity_score": score,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "not_connected",
                    "message": "Market intelligence not initialized",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            self.logger.error(f"Failed to get opportunity score: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_recommended_markets(self, product: str, limit: int = 5) -> Dict[str, Any]:
        """
        Get recommended markets for a product.
        
        Args:
            product: Product identifier
            limit: Maximum number of recommendations
            
        Returns:
            Recommended markets dictionary
        """
        try:
            if self.market_intel:
                markets = self.market_intel.get_recommended_markets(product, limit)
                return {
                    "status": "success",
                    "product": product,
                    "markets": markets,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "not_connected",
                    "message": "Market intelligence not initialized",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            self.logger.error(f"Failed to get recommended markets: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_optimization_recommendations(self) -> Dict[str, Any]:
        """
        Get optimization recommendations from market intelligence.
        
        Returns:
            Optimization recommendations dictionary
        """
        try:
            if self.market_intel:
                templates = self.market_intel.optimize_templates()
                targeting = self.market_intel.optimize_targeting()
                
                return {
                    "status": "success",
                    "templates": templates,
                    "targeting": targeting,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "not_connected",
                    "message": "Market intelligence not initialized",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            self.logger.error(f"Failed to get optimization recommendations: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def record_market_metric(self, metric_name: str, value: float, unit: str = "score", tags: Dict[str, str] = None) -> bool:
        """
        Record market intelligence metric.
        
        Args:
            metric_name: Metric name
            value: Metric value
            unit: Metric unit
            tags: Optional tags
            
        Returns:
            True if recorded successfully, False otherwise
        """
        try:
            metric = MissionMetric(
                metric_id=f"mi-{metric_name}-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                name=f"market_intelligence.{metric_name}",
                value=value,
                unit=unit,
                tags=tags or {}
            )
            
            from mission_control.repositories.mission_repository import MissionRepository
            repo = MissionRepository(self.mission_controller.db)
            return repo.record_metric(metric)
        except Exception as e:
            self.logger.error(f"Failed to record market metric: {e}")
            return False
