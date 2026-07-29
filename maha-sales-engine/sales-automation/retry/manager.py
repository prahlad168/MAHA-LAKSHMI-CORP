#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Retry Manager
Retry policies and circuit breaker implementation.
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.sales-automation.retry")


class RetryPolicy(Enum):
    IMMEDIATE = "immediate"
    LINEAR = "linear"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    ADAPTIVE = "adaptive"


class CircuitBreakerState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class RetryManager:
    """Manage retry logic for failed operations"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self._policies: Dict[str, Dict[str, Any]] = {}
        self._circuit_breakers: Dict[str, Dict[str, Any]] = {}
    
    def register_policy(self, operation: str, policy: RetryPolicy = RetryPolicy.EXPONENTIAL_BACKOFF,
                       max_retries: int = 3, initial_delay: float = 1.0,
                       backoff_factor: float = 2.0, max_delay: float = 60.0):
        self._policies[operation] = {
            "policy": policy.value,
            "max_retries": max_retries,
            "initial_delay": initial_delay,
            "backoff_factor": backoff_factor,
            "max_delay": max_delay
        }
    
    def get_delay(self, operation: str, retry_count: int) -> float:
        policy = self._policies.get(operation, {})
        policy_type = policy.get("policy", RetryPolicy.EXPONENTIAL_BACKOFF.value)
        initial_delay = policy.get("initial_delay", 1.0)
        backoff_factor = policy.get("backoff_factor", 2.0)
        max_delay = policy.get("max_delay", 60.0)
        
        if policy_type == RetryPolicy.IMMEDIATE.value:
            return 0.0
        elif policy_type == RetryPolicy.LINEAR.value:
            delay = initial_delay * retry_count
        elif policy_type == RetryPolicy.EXPONENTIAL_BACKOFF.value:
            delay = initial_delay * (backoff_factor ** retry_count)
        else:
            delay = initial_delay * (backoff_factor ** retry_count)
        
        return min(delay, max_delay)
    
    def should_retry(self, operation: str, retry_count: int, error: Optional[str] = None) -> bool:
        policy = self._policies.get(operation, {})
        max_retries = policy.get("max_retries", 3)
        
        if retry_count >= max_retries:
            return False
        
        if error and self._is_circuit_open(operation, error):
            return False
        
        return True
    
    def _is_circuit_open(self, operation: str, error: str) -> bool:
        breaker = self._circuit_breakers.get(operation)
        if not breaker:
            return False
        
        if breaker["state"] == CircuitBreakerState.OPEN.value:
            last_failure = datetime.fromisoformat(breaker["last_failure"])
            recovery_time = breaker.get("recovery_time", 60)
            if (datetime.now() - last_failure).total_seconds() > recovery_time:
                breaker["state"] = CircuitBreakerState.HALF_OPEN.value
                return False
            return True
        
        return False
    
    def record_success(self, operation: str):
        if operation in self._circuit_breakers:
            self._circuit_breakers[operation]["state"] = CircuitBreakerState.CLOSED.value
            self._circuit_breakers[operation]["failure_count"] = 0
    
    def record_failure(self, operation: str, error: str):
        if operation not in self._circuit_breakers:
            self._circuit_breakers[operation] = {
                "state": CircuitBreakerState.CLOSED.value,
                "failure_count": 0,
                "last_failure": None,
                "recovery_time": 60
            }
        
        breaker = self._circuit_breakers[operation]
        breaker["failure_count"] += 1
        breaker["last_failure"] = datetime.now().isoformat()
        
        threshold = self._policies.get(operation, {}).get("failure_threshold", 5)
        if breaker["failure_count"] >= threshold:
            breaker["state"] = CircuitBreakerState.OPEN.value
            logger.warning(f"Circuit breaker opened for {operation}")


def main():
    manager = RetryManager(None)
    manager.register_policy("publish", max_retries=3)
    print("Retry Manager initialized")


if __name__ == "__main__":
    main()
