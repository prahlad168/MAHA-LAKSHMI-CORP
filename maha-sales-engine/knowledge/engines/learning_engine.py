#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Learning Engine
Continuously learns from operational data, decisions, experiments, and customer behavior.
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
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.knowledge.learning")


class LearningEventType(Enum):
    RECOMMENDATION_APPROVED = "recommendation_approved"
    RECOMMENDATION_REJECTED = "recommendation_rejected"
    OPTIMIZATION_EXECUTED = "optimization_executed"
    ROLLBACK = "rollback"
    REVENUE_CHANGE = "revenue_change"
    CAMPAIGN_OUTCOME = "campaign_outcome"
    MARKETPLACE_PERFORMANCE = "marketplace_performance"
    CUSTOMER_BEHAVIOR = "customer_behavior"
    DECISION_MADE = "decision_made"


@dataclass
class LearningEvent:
    event_id: str
    event_type: LearningEventType
    source: str
    data: Dict[str, Any]
    outcome: Dict[str, Any]
    reward: float
    context: Dict[str, Any]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class LearningInsight:
    insight_id: str
    category: str
    pattern: str
    confidence: float
    recommendation: str
    supporting_evidence: List[str]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class LearningEngine:
    """
    Learning engine that continuously learns from operational data.
    """
    
    def __init__(self, db_manager):
        self.db = db_manager
        self._events: List[LearningEvent] = []
        self._insights: Dict[str, LearningInsight] = {}
        self._performance_by_category: Dict[str, List[float]] = defaultdict(list)
    
    def record_event(self, event_type: LearningEventType, source: str, data: Dict[str, Any], outcome: Dict[str, Any], reward: float, context: Dict[str, Any]):
        """Record learning event"""
        event_id = f"learn-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
        
        event = LearningEvent(
            event_id=event_id,
            event_type=event_type,
            source=source,
            data=data,
            outcome=outcome,
            reward=reward,
            context=context
        )
        
        self._events.append(event)
        
        # Update performance tracking
        category = context.get("category", "general")
        self._performance_by_category[category].append(reward)
        
        # Generate insights if enough data
        self._generate_insights(category)
        
        logger.info(f"Learning event recorded: {event_id} ({event_type.value})")
        return event_id
    
    def _generate_insights(self, category: str):
        """Generate insights from learning data"""
        rewards = self._performance_by_category.get(category, [])
        if len(rewards) < 5:
            return
        
        avg_reward = sum(rewards) / len(rewards)
        
        if avg_reward > 0.7:
            insight = LearningInsight(
                insight_id=f"insight-{uuid.uuid4().hex[:8]}",
                category=category,
                pattern="high_performance",
                confidence=min(0.95, avg_reward + 0.1),
                recommendation="Continue current strategy and increase execution frequency",
                supporting_evidence=[f"Average reward: {avg_reward:.2f}", f"Sample size: {len(rewards)}"]
            )
            self._insights[insight.insight_id] = insight
        elif avg_reward < 0.3:
            insight = LearningInsight(
                insight_id=f"insight-{uuid.uuid4().hex[:8]}",
                category=category,
                pattern="low_performance",
                confidence=min(0.95, 1.0 - avg_reward),
                recommendation="Pause optimizations and review strategy",
                supporting_evidence=[f"Average reward: {avg_reward:.2f}", f"Sample size: {len(rewards)}"]
            )
            self._insights[insight.insight_id] = insight
    
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
    
    def get_insights(self, category: Optional[str] = None) -> List[LearningInsight]:
        """Get learning insights"""
        insights = list(self._insights.values())
        if category:
            insights = [i for i in insights if i.category == category]
        return insights


def main():
    print("Learning Engine loaded")


if __name__ == "__main__":
    main()
