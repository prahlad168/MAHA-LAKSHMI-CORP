#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Experiment Engine
Supports A/B testing, canary rollout, shadow mode, gradual rollout, and automatic rollback.
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
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.optimization.experiment")


class ExperimentType(Enum):
    A_B_TEST = "a_b_test"
    CANARY = "canary"
    SHADOW = "shadow"
    GRADUAL = "gradual"


class ExperimentStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class Experiment:
    experiment_id: str
    optimization_id: str
    experiment_type: ExperimentType
    status: ExperimentStatus
    config: Dict[str, Any]
    results: Dict[str, Any] = field(default_factory=dict)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class ExperimentEngine:
    """
    Experiment engine for safe optimization testing.
    """
    
    def __init__(self, db_manager, rollback_engine):
        self.db = db_manager
        self.rollback_engine = rollback_engine
        self._experiments: Dict[str, Experiment] = {}
    
    def create_experiment(self, optimization_id: str, experiment_type: ExperimentType, config: Dict[str, Any]) -> Experiment:
        """Create experiment"""
        experiment_id = f"exp-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
        
        experiment = Experiment(
            experiment_id=experiment_id,
            optimization_id=optimization_id,
            experiment_type=experiment_type,
            status=ExperimentStatus.PENDING,
            config=config
        )
        
        self._experiments[experiment_id] = experiment
        logger.info(f"Experiment created: {experiment_id} ({experiment_type.value})")
        return experiment
    
    def start_experiment(self, experiment_id: str) -> bool:
        """Start experiment"""
        experiment = self._experiments.get(experiment_id)
        if not experiment:
            return False
        
        experiment.status = ExperimentStatus.RUNNING
        experiment.started_at = datetime.now().isoformat()
        logger.info(f"Experiment started: {experiment_id}")
        return True
    
    def complete_experiment(self, experiment_id: str, results: Dict[str, Any]) -> bool:
        """Complete experiment"""
        experiment = self._experiments.get(experiment_id)
        if not experiment:
            return False
        
        experiment.status = ExperimentStatus.COMPLETED
        experiment.results = results
        experiment.completed_at = datetime.now().isoformat()
        logger.info(f"Experiment completed: {experiment_id}")
        return True
    
    def rollback_experiment(self, experiment_id: str, reason: str) -> bool:
        """Rollback experiment"""
        experiment = self._experiments.get(experiment_id)
        if not experiment:
            return False
        
        experiment.status = ExperimentStatus.ROLLED_BACK
        
        # Execute rollback
        self.rollback_engine.rollback(experiment.optimization_id, reason)
        
        logger.info(f"Experiment rolled back: {experiment_id}")
        return True


def main():
    print("Experiment Engine loaded")


if __name__ == "__main__":
    main()
