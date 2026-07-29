#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Decision Memory
Stores and retrieves decision history for learning and explainability.
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

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.knowledge.decision_memory")


@dataclass
class DecisionMemory:
    memory_id: str
    decision_id: str
    optimization_id: str
    category: str
    decision: str
    reason: str
    evidence: Dict[str, Any]
    confidence: float
    risk_score: float
    outcome: Dict[str, Any]
    reward: float
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class DecisionMemoryEngine:
    """
    Decision memory engine.
    Stores decisions for learning and explainability.
    """
    
    def __init__(self, db_manager):
        self.db = db_manager
        self._memories: Dict[str, DecisionMemory] = {}
    
    def store(self, decision_id: str, optimization_id: str, category: str, decision: str, reason: str, evidence: Dict[str, Any], confidence: float, risk_score: float) -> DecisionMemory:
        """Store decision memory"""
        memory_id = f"dm-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
        
        memory = DecisionMemory(
            memory_id=memory_id,
            decision_id=decision_id,
            optimization_id=optimization_id,
            category=category,
            decision=decision,
            reason=reason,
            evidence=evidence,
            confidence=confidence,
            risk_score=risk_score,
            outcome={},
            reward=0.0
        )
        
        self._memories[memory_id] = memory
        logger.info(f"Decision memory stored: {memory_id}")
        return memory
    
    def update_outcome(self, memory_id: str, outcome: Dict[str, Any], reward: float) -> Optional[DecisionMemory]:
        """Update decision outcome"""
        memory = self._memories.get(memory_id)
        if memory:
            memory.outcome = outcome
            memory.reward = reward
            logger.info(f"Decision outcome updated: {memory_id}")
        return memory
    
    def get_by_category(self, category: str) -> List[DecisionMemory]:
        """Get decisions by category"""
        return [m for m in self._memories.values() if m.category == category]
    
    def get(self, memory_id: str) -> Optional[DecisionMemory]:
        """Get decision memory by ID"""
        return self._memories.get(memory_id)
    
    def get_learning_data(self) -> List[Dict[str, Any]]:
        """Get data for learning"""
        return [
            {
                "category": m.category,
                "confidence": m.confidence,
                "risk_score": m.risk_score,
                "reward": m.reward,
                "evidence": m.evidence
            }
            for m in self._memories.values()
        ]


def main():
    print("Decision Memory loaded")


if __name__ == "__main__":
    main()
