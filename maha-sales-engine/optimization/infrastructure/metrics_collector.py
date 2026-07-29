#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Metrics Collector
Collects optimization metrics for observability.
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.optimization.metrics")


@dataclass
class OptimizationMetrics:
    recommendations_generated: int = 0
    recommendations_approved: int = 0
    recommendations_rejected: int = 0
    optimizations_executed: int = 0
    rollback_count: int = 0
    simulation_accuracy: float = 0.0
    average_confidence: float = 0.0
    revenue_improvement: float = 0.0


class MetricsCollector:
    """
    Metrics collector for optimization engine observability.
    """
    
    def __init__(self):
        self._metrics = OptimizationMetrics()
        self._confidence_scores: List[float] = []
        self._revenue_improvements: List[float] = []
    
    def record_recommendation_generated(self):
        self._metrics.recommendations_generated += 1
    
    def record_recommendation_approved(self):
        self._metrics.recommendations_approved += 1
    
    def record_recommendation_rejected(self):
        self._metrics.recommendations_rejected += 1
    
    def record_optimization_executed(self):
        self._metrics.optimizations_executed += 1
    
    def record_rollback(self):
        self._metrics.rollback_count += 1
    
    def record_confidence(self, confidence: float):
        self._confidence_scores.append(confidence)
        self._metrics.average_confidence = sum(self._confidence_scores) / len(self._confidence_scores)
    
    def record_revenue_improvement(self, improvement: float):
        self._revenue_improvements.append(improvement)
        self._metrics.revenue_improvement = sum(self._revenue_improvements)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return {
            "recommendations_generated": self._metrics.recommendations_generated,
            "recommendations_approved": self._metrics.recommendations_approved,
            "recommendations_rejected": self._metrics.recommendations_rejected,
            "optimizations_executed": self._metrics.optimizations_executed,
            "rollback_count": self._metrics.rollback_count,
            "average_confidence": round(self._metrics.average_confidence, 2),
            "revenue_improvement": round(self._metrics.revenue_improvement, 2)
        }


def main():
    print("Metrics Collector loaded")


if __name__ == "__main__":
    main()
