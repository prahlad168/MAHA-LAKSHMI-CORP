#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Marketplace Connector Metrics
Collects marketplace connector metrics.
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

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.marketplace_connector.metrics")


@dataclass
class ConnectorMetrics:
    total_publications: int = 0
    successful_publications: int = 0
    failed_publications: int = 0
    retry_count: int = 0
    avg_publication_time: float = 0.0
    queue_depth: int = 0
    dead_letter_count: int = 0


class MetricsCollector:
    """
    Metrics collector for marketplace connector.
    """
    
    def __init__(self):
        self._metrics = ConnectorMetrics()
        self._publication_times: List[float] = []
    
    def record_publication_attempt(self):
        self._metrics.total_publications += 1
    
    def record_publication_success(self):
        self._metrics.successful_publications += 1
    
    def record_publication_failure(self):
        self._metrics.failed_publications += 1
    
    def record_retry(self):
        self._metrics.retry_count += 1
    
    def record_publication_time(self, duration: float):
        self._publication_times.append(duration)
        self._metrics.avg_publication_time = sum(self._publication_times) / len(self._publication_times)
    
    def update_queue_depth(self, depth: int):
        self._metrics.queue_depth = depth
    
    def update_dead_letter_count(self, count: int):
        self._metrics.dead_letter_count = count
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return {
            "total_publications": self._metrics.total_publications,
            "successful_publications": self._metrics.successful_publications,
            "failed_publications": self._metrics.failed_publications,
            "retry_count": self._metrics.retry_count,
            "avg_publication_time": round(self._metrics.avg_publication_time, 2),
            "queue_depth": self._metrics.queue_depth,
            "dead_letter_count": self._metrics.dead_letter_count,
            "success_rate": round(self._metrics.successful_publications / self._metrics.total_publications, 2) if self._metrics.total_publications > 0 else 0.0
        }


def main():
    print("Metrics Collector loaded")


if __name__ == "__main__":
    main()
