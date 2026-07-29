#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Metrics Collector
Observability and metrics collection.
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.sales-automation.metrics")


class MetricsCollector:
    """Collect and aggregate operational metrics"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self._metrics: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self._counters: Dict[str, int] = defaultdict(int)
        self._timers: Dict[str, List[float]] = defaultdict(list)
    
    def increment(self, metric_name: str, value: int = 1, tags: Dict[str, str] = None):
        self._counters[metric_name] += value
        self._record_metric(metric_name, "counter", value, tags)
    
    def timing(self, metric_name: str, duration_ms: float, tags: Dict[str, str] = None):
        self._timers[metric_name].append(duration_ms)
        self._record_metric(metric_name, "timer", duration_ms, tags)
    
    def gauge(self, metric_name: str, value: float, tags: Dict[str, str] = None):
        self._record_metric(metric_name, "gauge", value, tags)
    
    def get_metrics(self, metric_name: str = None) -> Dict[str, Any]:
        result = {}
        
        if metric_name:
            counters = {metric_name: self._counters.get(metric_name, 0)}
            timers = {metric_name: self._calculate_timer_stats(metric_name)}
        else:
            counters = dict(self._counters)
            timers = {name: self._calculate_timer_stats(name) for name in self._timers}
        
        result["counters"] = counters
        result["timers"] = timers
        
        return result
    
    def _calculate_timer_stats(self, metric_name: str) -> Dict[str, float]:
        values = self._timers.get(metric_name, [])
        if not values:
            return {"count": 0, "avg": 0, "min": 0, "max": 0}
        
        return {
            "count": len(values),
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values)
        }
    
    def _record_metric(self, metric_name: str, metric_type: str, value: Any, tags: Dict[str, str] = None):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO automation_metrics (metric_name, metric_type, value, tags, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                metric_name, metric_type, str(value),
                json.dumps(tags or {}), datetime.now().isoformat()
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to record metric: {e}")


def main():
    print("Metrics Collector initialized")


if __name__ == "__main__":
    main()
