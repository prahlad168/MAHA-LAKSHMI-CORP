#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Learning Engine
Accumulates experience and improves optimization strategies over time.
"""

import os
import sys
import json
import time
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.optimization.learning")


@dataclass
class LearningRecord:
    record_id: str
    optimization_id: str
    category: str
    action: str
    outcome: Dict[str, Any]
    reward: float
    context: Dict[str, Any]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class LearningEngine:
    """
    Learning engine that accumulates experience and improves optimization.
    """
    
    def __init__(self, db_manager):
        self.db = db_manager
        self._records: List[LearningRecord] = []
        self._performance_by_category: Dict[str, List[float]] = defaultdict(list)
    
    def record(self, optimization_id: str, category: str, action: str, outcome: Dict[str, Any], reward: float, context: Dict[str, Any]):
        """Record learning experience"""
        record_id = f"learn-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
        
        record = LearningRecord(
            record_id=record_id,
            optimization_id=optimization_id,
            category=category,
            action=action,
            outcome=outcome,
            reward=reward,
            context=context
        )
        
        self._records.append(record)
        self._performance_by_category[category].append(reward)
        
        logger.info(f"Learning recorded: {record_id} for {category}")
    
    def get_performance(self, category: str) -> Dict[str, float]:
        """Get performance metrics for category"""
        rewards = self._performance_by_category.get(category, [])
        if not rewards:
            return {"avg_reward": 0.0, "count": 0}
        
        return {
            "avg_reward": sum(rewards) / len(rewards),
            "count": len(rewards),
            "min_reward": min(rewards),
            "max_reward": max(rewards)
        }
    
    def get_recommendations(self, category: str) -> List[str]:
        """Get learning-based recommendations"""
        performance = self.get_performance(category)
        
        if performance["avg_reward"] > 0.7:
            return ["Continue current strategy", "Increase execution frequency"]
        elif performance["avg_reward"] > 0.4:
            return ["Adjust parameters", "Test alternative approaches"]
        else:
            return ["Pause optimizations", "Review strategy", "Run diagnostics"]


def main():
    print("Learning Engine loaded")


if __name__ == "__main__":
    main()
