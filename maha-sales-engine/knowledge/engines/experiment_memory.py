#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Experiment Memory
Stores experiment results for learning.
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

logger = logging.getLogger("maha-sales-engine.knowledge.experiment_memory")


@dataclass
class ExperimentMemory:
    memory_id: str
    experiment_id: str
    optimization_id: str
    experiment_type: str
    config: Dict[str, Any]
    results: Dict[str, Any]
    success: bool
    reward: float
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class ExperimentMemoryEngine:
    """
    Experiment memory engine.
    Stores experiment results for learning.
    """
    
    def __init__(self, db_manager):
        self.db = db_manager
        self._memories: Dict[str, ExperimentMemory] = {}
    
    def store(self, experiment_id: str, optimization_id: str, experiment_type: str, config: Dict[str, Any], results: Dict[str, Any], success: bool, reward: float) -> ExperimentMemory:
        """Store experiment memory"""
        memory_id = f"em-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
        
        memory = ExperimentMemory(
            memory_id=memory_id,
            experiment_id=experiment_id,
            optimization_id=optimization_id,
            experiment_type=experiment_type,
            config=config,
            results=results,
            success=success,
            reward=reward
        )
        
        self._memories[memory_id] = memory
        logger.info(f"Experiment memory stored: {memory_id}")
        return memory
    
    def get_by_type(self, experiment_type: str) -> List[ExperimentMemory]:
        """Get experiments by type"""
        return [m for m in self._memories.values() if m.experiment_type == experiment_type]
    
    def get_success_rate(self, experiment_type: str) -> float:
        """Get success rate for experiment type"""
        experiments = self.get_by_type(experiment_type)
        if not experiments:
            return 0.0
        
        successes = sum(1 for e in experiments if e.success)
        return successes / len(experiments)


def main():
    print("Experiment Memory loaded")


if __name__ == "__main__":
    main()
