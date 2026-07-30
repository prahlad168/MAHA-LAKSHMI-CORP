#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Marketing Job Queue
Job queue for marketing operations.
"""

import json
import logging
import threading
import time
import uuid
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from queue import PriorityQueue, Empty
from enum import Enum

logger = logging.getLogger("maha-sales-engine.marketing.queue")


class JobState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    RETRY = "retry"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class JobPriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class Job:
    """Job data structure"""
    job_id: str
    job_type: str
    priority: int
    state: str
    payload: Dict[str, Any]
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


class MarketingJobQueue:
    """Job queue for marketing operations"""
    
    def __init__(self, max_workers: int = 3):
        self._queue = PriorityQueue()
        self._jobs: Dict[str, Job] = {}
        self._workers: List[threading.Thread] = []
        self._max_workers = max_workers
        self._running = False
        self._lock = threading.Lock()
        self._handlers: Dict[str, Callable] = {}
    
    def start(self):
        """Start job queue workers"""
        if self._running:
            return
        self._running = True
        for i in range(self._max_workers):
            worker = threading.Thread(target=self._worker_loop, args=(i,), daemon=True)
            worker.start()
            self._workers.append(worker)
        logger.info(f"Marketing job queue started with {self._max_workers} workers")
    
    def stop(self):
        """Stop job queue"""
        self._running = False
        for worker in self._workers:
            worker.join(timeout=5)
        logger.info("Marketing job queue stopped")
    
    def enqueue(self, job_type: str, payload: Dict[str, Any], 
                priority: JobPriority = JobPriority.NORMAL,
                max_retries: int = 3) -> str:
        """Add job to queue"""
        job_id = f"mkt-job-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        job = Job(
            job_id=job_id,
            job_type=job_type,
            priority=priority.value,
            state=JobState.PENDING.value,
            payload=payload,
            created_at=datetime.now().isoformat(),
            max_retries=max_retries
        )
        with self._lock:
            self._jobs[job_id] = job
            self._queue.put((priority.value, job.created_at, job_id))
        logger.info(f"Marketing job enqueued: {job_id} ({job_type})")
        return job_id
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID"""
        job = self._jobs.get(job_id)
        if job:
            return {
                "job_id": job.job_id,
                "job_type": job.job_type,
                "state": job.state,
                "created_at": job.created_at,
                "started_at": job.started_at,
                "completed_at": job.completed_at,
                "retry_count": job.retry_count,
                "error_message": job.error_message
            }
        return None
    
    def register_handler(self, job_type: str, handler: Callable):
        """Register handler for job type"""
        self._handlers[job_type] = handler
    
    def _worker_loop(self, worker_id: int):
        """Worker thread loop"""
        while self._running:
            try:
                priority, created_at, job_id = self._queue.get(timeout=1)
                self._process_job(job_id, worker_id)
            except Empty:
                continue
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
    
    def _process_job(self, job_id: str, worker_id: int):
        """Process a single job"""
        job = self._jobs.get(job_id)
        if not job or job.state == JobState.CANCELLED.value:
            return
        
        job.state = JobState.RUNNING.value
        job.started_at = datetime.now().isoformat()
        
        try:
            handler = self._handlers.get(job.job_type)
            if not handler:
                raise ValueError(f"No handler for job type: {job.job_type}")
            result = handler(job.payload)
            job.state = JobState.COMPLETED.value
            job.completed_at = datetime.now().isoformat()
            job.result = result
            logger.info(f"Marketing job completed: {job_id}")
        except Exception as e:
            job.error_message = str(e)
            job.retry_count += 1
            if job.retry_count < job.max_retries:
                job.state = JobState.RETRY.value
                time.sleep(2 ** job.retry_count)
                self._queue.put((job.priority, job.created_at, job_id))
            else:
                job.state = JobState.FAILED.value
                logger.error(f"Marketing job failed permanently: {job_id} - {e}")


def main():
    """Test marketing job queue"""
    queue = MarketingJobQueue(max_workers=2)
    queue.start()
    
    def handler(payload):
        return {"success": True}
    
    queue.register_handler("generate_marketing", handler)
    job_id = queue.enqueue("generate_marketing", {"product_id": "test-123"})
    time.sleep(2)
    job = queue.get_job(job_id)
    print(f"Job: {job}")
    queue.stop()


if __name__ == "__main__":
    main()
