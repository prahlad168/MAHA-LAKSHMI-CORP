#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Pattern Recognition
Identifies patterns in operational data, customer behavior, and business outcomes.
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

logger = logging.getLogger("maha-sales-engine.knowledge.pattern")


class PatternType(Enum):
    TREND = "trend"
    ANOMALY = "anomaly"
    CORRELATION = "correlation"
    SEASONALITY = "seasonality"
    THRESHOLD = "threshold"


@dataclass
class Pattern:
    pattern_id: str
    pattern_type: PatternType
    name: str
    description: str
    confidence: float
    data_points: int
    evidence: Dict[str, Any]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


class PatternRecognition:
    """
    Pattern recognition engine.
    Identifies patterns in operational data.
    """
    
    def __init__(self, db_manager):
        self.db = db_manager
        self._patterns: Dict[str, Pattern] = {}
    
    def detect_trend(self, metric_name: str, values: List[float]) -> Optional[Pattern]:
        """Detect trend in metric values"""
        if len(values) < 3:
            return None
        
        # Simple trend detection
        increases = sum(1 for i in range(len(values)-1) if values[i+1] > values[i])
        trend_strength = increases / (len(values) - 1)
        
        if trend_strength > 0.7:
            pattern_id = f"pattern-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
            pattern = Pattern(
                pattern_id=pattern_id,
                pattern_type=PatternType.TREND,
                name=f"Upward Trend: {metric_name}",
                description=f"Metric {metric_name} shows strong upward trend",
                confidence=trend_strength,
                data_points=len(values),
                evidence={"values": values, "trend_strength": trend_strength}
            )
            self._patterns[pattern_id] = pattern
            logger.info(f"Trend detected: {pattern_id}")
            return pattern
        
        return None
    
    def detect_anomaly(self, metric_name: str, current_value: float, historical_values: List[float], threshold: float = 2.0) -> Optional[Pattern]:
        """Detect anomaly in metric values"""
        if len(historical_values) < 5:
            return None
        
        mean = sum(historical_values) / len(historical_values)
        variance = sum((x - mean) ** 2 for x in historical_values) / len(historical_values)
        std_dev = variance ** 0.5
        
        if std_dev == 0:
            return None
        
        z_score = abs(current_value - mean) / std_dev
        
        if z_score > threshold:
            pattern_id = f"pattern-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
            pattern = Pattern(
                pattern_id=pattern_id,
                pattern_type=PatternType.ANOMALY,
                name=f"Anomaly: {metric_name}",
                description=f"Metric {metric_name} shows anomalous value",
                confidence=min(0.99, z_score / 3.0),
                data_points=len(historical_values),
                evidence={
                    "current_value": current_value,
                    "mean": mean,
                    "std_dev": std_dev,
                    "z_score": z_score
                }
            )
            self._patterns[pattern_id] = pattern
            logger.info(f"Anomaly detected: {pattern_id}")
            return pattern
        
        return None
    
    def get_patterns(self, pattern_type: Optional[PatternType] = None) -> List[Pattern]:
        """Get detected patterns"""
        patterns = list(self._patterns.values())
        if pattern_type:
            patterns = [p for p in patterns if p.pattern_type == pattern_type]
        return patterns


def main():
    print("Pattern Recognition loaded")


if __name__ == "__main__":
    main()
