#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Knowledge Metrics
Collects knowledge platform metrics.
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

logger = logging.getLogger("maha-sales-engine.knowledge.metrics")


@dataclass
class KnowledgeMetrics:
    total_knowledge_items: int = 0
    total_decisions: int = 0
    total_experiments: int = 0
    total_patterns: int = 0
    total_insights: int = 0
    avg_confidence: float = 0.0
    search_queries: int = 0
    learning_events: int = 0


class KnowledgeMetricsCollector:
    """
    Metrics collector for knowledge platform.
    """
    
    def __init__(self):
        self._metrics = KnowledgeMetrics()
        self._confidence_scores: List[float] = []
    
    def record_knowledge_created(self):
        self._metrics.total_knowledge_items += 1
    
    def record_decision(self):
        self._metrics.total_decisions += 1
    
    def record_experiment(self):
        self._metrics.total_experiments += 1
    
    def record_pattern(self):
        self._metrics.total_patterns += 1
    
    def record_insight(self):
        self._metrics.total_insights += 1
    
    def record_confidence(self, confidence: float):
        self._confidence_scores.append(confidence)
        self._metrics.avg_confidence = sum(self._confidence_scores) / len(self._confidence_scores)
    
    def record_search(self):
        self._metrics.search_queries += 1
    
    def record_learning_event(self):
        self._metrics.learning_events += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return {
            "total_knowledge_items": self._metrics.total_knowledge_items,
            "total_decisions": self._metrics.total_decisions,
            "total_experiments": self._metrics.total_experiments,
            "total_patterns": self._metrics.total_patterns,
            "total_insights": self._metrics.total_insights,
            "avg_confidence": round(self._metrics.avg_confidence, 2),
            "search_queries": self._metrics.search_queries,
            "learning_events": self._metrics.learning_events
        }


def main():
    print("Knowledge Metrics loaded")


if __name__ == "__main__":
    main()
