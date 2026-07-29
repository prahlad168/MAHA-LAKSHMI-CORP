#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Retry Engine
Handles retry logic for failed publications.
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

logger = logging.getLogger("maha-sales-engine.marketplace_connector.retry")


class RetryStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"


@dataclass
class RetryJob:
    job_id: str
    publication_id: str
    attempt: int
    max_attempts: int
    error: str
    status: RetryStatus
    next_retry: Optional[str]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


class RetryEngine:
    """
    Retry engine for failed publications.
    """
    
    def __init__(self, max_attempts: int = 3, backoff_factor: float = 2.0):
        self.max_attempts = max_attempts
        self.backoff_factor = backoff_factor
        self._retry_queue: List[RetryJob] = []
        self._dead_letter_queue: List[RetryJob] = []
    
    def enqueue(self, publication_id: str, error: str) -> RetryJob:
        """Enqueue failed publication for retry"""
        job_id = f"retry-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
        
        job = RetryJob(
            job_id=job_id,
            publication_id=publication_id,
            attempt=1,
            max_attempts=self.max_attempts,
            error=error,
            status=RetryStatus.PENDING,
            next_retry=(datetime.now() + timedelta(minutes=1)).isoformat()
        )
        
        self._retry_queue.append(job)
        logger.info(f"Retry job enqueued: {job_id}")
        return job
    
    def process_retries(self, processor) -> Dict[str, int]:
        """Process retry queue"""
        results = {"processed": 0, "succeeded": 0, "failed": 0}
        
        for job in list(self._retry_queue):
            if job.status != RetryStatus.PENDING:
                continue
            
            # Check if ready for retry
            if job.next_retry and datetime.now() < datetime.fromisoformat(job.next_retry):
                continue
            
            # Process retry
            job.status = RetryStatus.PROCESSING
            try:
                result = processor(job.publication_id)
                if result.get("success"):
                    job.status = RetryStatus.COMPLETED
                    results["succeeded"] += 1
                else:
                    raise Exception(result.get("error", "Retry failed"))
            except Exception as e:
                job.attempt += 1
                job.error = str(e)
                
                if job.attempt >= job.max_attempts:
                    job.status = RetryStatus.DEAD_LETTER
                    self._dead_letter_queue.append(job)
                    results["failed"] += 1
                else:
                    job.status = RetryStatus.PENDING
                    job.next_retry = (datetime.now() + timedelta(minutes=self.backoff_factor ** job.attempt)).isoformat()
                    results["failed"] += 1
            
            results["processed"] += 1
        
        return results
    
    def get_retry_queue(self) -> List[RetryJob]:
        """Get current retry queue"""
        return [j for j in self._retry_queue if j.status == RetryStatus.PENDING]
    
    def get_dead_letter_queue(self) -> List[RetryJob]:
        """Get dead letter queue"""
        return self._dead_letter_queue.copy()


from datetime import timedelta


def main():
    print("Retry Engine loaded")


if __name__ == "__main__":
    main()
