#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Confidence Engine
Calculates confidence scores for optimization recommendations.
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
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.optimization.confidence")


@dataclass
class ConfidenceScore:
    score: float
    factors: Dict[str, float]
    explanation: str
    calculated_at: str = field(default_factory=lambda: datetime.now().isoformat())


class ConfidenceEngine:
    """
    Confidence engine that calculates confidence scores for optimizations.
    Recommendations below configurable thresholds must never execute automatically.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.min_confidence = self.config.get("min_confidence", 0.6)
        self.weights = self.config.get("weights", {
            "historical_accuracy": 0.3,
            "data_quality": 0.2,
            "sample_size": 0.2,
            "simulation_consistency": 0.2,
            "market_stability": 0.1
        })
    
    def calculate(self, optimization_context, optimizer_result: Dict[str, Any]) -> float:
        """
        Calculate confidence score for optimization.
        Returns score between 0.0 and 1.0.
        """
        factors = {}
        
        # Historical accuracy factor
        factors["historical_accuracy"] = self._calculate_historical_accuracy(optimizer_result)
        
        # Data quality factor
        factors["data_quality"] = self._calculate_data_quality(optimizer_result)
        
        # Sample size factor
        factors["sample_size"] = self._calculate_sample_size(optimizer_result)
        
        # Simulation consistency factor
        factors["simulation_consistency"] = self._calculate_simulation_consistency(optimizer_result)
        
        # Market stability factor
        factors["market_stability"] = self._calculate_market_stability(optimizer_result)
        
        # Calculate weighted score
        score = sum(factors.get(factor, 0.0) * weight for factor, weight in self.weights.items())
        score = max(0.0, min(1.0, score))  # Clamp to 0-1
        
        logger.info(f"Confidence score calculated: {score:.2f} for {optimization_context.optimization_id}")
        return score
    
    def _calculate_historical_accuracy(self, optimizer_result: Dict[str, Any]) -> float:
        """Calculate historical accuracy factor"""
        past_accuracy = optimizer_result.get("historical_accuracy", 0.7)
        return min(1.0, max(0.0, past_accuracy))
    
    def _calculate_data_quality(self, optimizer_result: Dict[str, Any]) -> float:
        """Calculate data quality factor"""
        data_points = optimizer_result.get("data_points", 100)
        missing_data = optimizer_result.get("missing_data_percent", 0.0)
        
        quality = 1.0 - missing_data
        if data_points < 10:
            quality *= 0.5
        elif data_points < 50:
            quality *= 0.8
        
        return min(1.0, max(0.0, quality))
    
    def _calculate_sample_size(self, optimizer_result: Dict[str, Any]) -> float:
        """Calculate sample size factor"""
        sample_size = optimizer_result.get("sample_size", 100)
        if sample_size >= 1000:
            return 1.0
        elif sample_size >= 100:
            return 0.8
        elif sample_size >= 10:
            return 0.5
        else:
            return 0.2
    
    def _calculate_simulation_consistency(self, optimizer_result: Dict[str, Any]) -> float:
        """Calculate simulation consistency factor"""
        simulation_variance = optimizer_result.get("simulation_variance", 0.1)
        return max(0.0, 1.0 - simulation_variance)
    
    def _calculate_market_stability(self, optimizer_result: Dict[str, Any]) -> float:
        """Calculate market stability factor"""
        market_volatility = optimizer_result.get("market_volatility", 0.2)
        return max(0.0, 1.0 - market_volatility)
    
    def is_confident(self, confidence: float) -> bool:
        """Check if confidence meets minimum threshold"""
        return confidence >= self.min_confidence


def main():
    print("Confidence Engine loaded")


if __name__ == "__main__":
    main()
