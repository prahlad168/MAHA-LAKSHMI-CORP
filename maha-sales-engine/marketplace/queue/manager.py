#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Marketplace Job Queue
Asynchronous job queue for marketplace operations.
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
from collections import defaultdict

logger = logging.getLogger("maha-sales-engine.marketplace.queue")


class JobState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    WAITING = "waiting"
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
    timeout: int = 300
    metadata: Dict[str, Any] = field(default_factory=dict)


class JobQueue:
    """Asynchronous job queue for marketplace operations"""
    
    def __init__(self, max_workers: int = 5):
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
        
        logger.info(f"Job queue started with {self._max_workers} workers")
    
    def stop(self):
        """Stop job queue"""
        self._running = False
        for worker in self._workers:
            worker.join(timeout=5)
        logger.info("Job queue stopped")
    
    def enqueue(self, job_type: str, payload: Dict[str, Any], 
                priority: JobPriority = JobPriority.NORMAL,
                max_retries: int = 3,
                timeout: int = 300) -> str:
        """Add job to queue"""
        job_id = f"job-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        job = Job(
            job_id=job_id,
            job_type=job_type,
            priority=priority.value,
            state=JobState.PENDING.value,
            payload=payload,
            created_at=datetime.now().isoformat(),
            max_retries=max_retries,
            timeout=timeout
        )
        
        with self._lock:
            self._jobs[job_id] = job
            self._queue.put((priority.value, job.created_at, job_id))
        
        logger.info(f"Job enqueued: {job_id} ({job_type})")
        return job_id
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID"""
        job = self._jobs.get(job_id)
        if job:
            return {
                "job_id": job.job_id,
                "job_type": job.job_type,
                "state": job.state,
                "priority": job.priority,
                "created_at": job.created_at,
                "started_at": job.started_at,
                "completed_at": job.completed_at,
                "retry_count": job.retry_count,
                "error_message": job.error_message
            }
        return None
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel pending job"""
        with self._lock:
            job = self._jobs.get(job_id)
            if job and job.state == JobState.PENDING.value:
                job.state = JobState.CANCELLED.value
                logger.info(f"Job cancelled: {job_id}")
                return True
        return False
    
    def register_handler(self, job_type: str, handler: Callable):
        """Register handler for job type"""
        self._handlers[job_type] = handler
        logger.debug(f"Handler registered for {job_type}")
    
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
        if not job:
            return
        
        if job.state == JobState.CANCELLED.value:
            return
        
        # Update state
        job.state = JobState.RUNNING.value
        job.started_at = datetime.now().isoformat()
        
        logger.info(f"Processing job {job_id} on worker {worker_id}")
        
        try:
            handler = self._handlers.get(job.job_type)
            if not handler:
                raise ValueError(f"No handler for job type: {job.job_type}")
            
            result = handler(job.payload)
            
            job.state = JobState.COMPLETED.value
            job.completed_at = datetime.now().isoformat()
            job.result = result
            
            logger.info(f"Job completed: {job_id}")
            
        except Exception as e:
            job.error_message = str(e)
            job.retry_count += 1
            
            if job.retry_count < job.max_retries:
                job.state = JobState.RETRY.value
                logger.warning(f"Job failed, retrying: {job_id} (attempt {job.retry_count})")
                time.sleep(2 ** job.retry_count)
                self._queue.put((job.priority, job.created_at, job_id))
            else:
                job.state = JobState.FAILED.value
                logger.error(f"Job failed permanently: {job_id} - {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        with self._lock:
            states = defaultdict(int)
            for job in self._jobs.values():
                states[job.state] += 1
            
            return {
                "total_jobs": len(self._jobs),
                "pending": states.get(JobState.PENDING.value, 0),
                "running": states.get(JobState.RUNNING.value, 0),
                "completed": states.get(JobState.COMPLETED.value, 0),
                "failed": states.get(JobState.FAILED.value, 0),
                "retry": states.get(JobState.RETRY.value, 0),
                "cancelled": states.get(JobState.CANCELLED.value, 0),
                "queue_size": self._queue.qsize()
            }


class RetryManager:
    """Manage retry logic for failed operations"""
    
    def __init__(self):
        self._retry_policies: Dict[str, Dict[str, Any]] = {}
    
    def register_policy(self, operation: str, max_retries: int = 3, 
                       backoff_factor: float = 2.0, 
                       initial_delay: float = 1.0):
        """Register retry policy for operation"""
        self._retry_policies[operation] = {
            "max_retries": max_retries,
            "backoff_factor": backoff_factor,
            "initial_delay": initial_delay
        }
    
    def get_delay(self, operation: str, retry_count: int) -> float:
        """Calculate retry delay"""
        policy = self._retry_policies.get(operation, {})
        initial_delay = policy.get("initial_delay", 1.0)
        backoff_factor = policy.get("backoff_factor", 2.0)
        
        return initial_delay * (backoff_factor ** retry_count)
    
    def should_retry(self, operation: str, retry_count: int) -> bool:
        """Check if operation should be retried"""
        policy = self._retry_policies.get(operation, {})
        max_retries = policy.get("max_retries", 3)
        return retry_count < max_retries


def main():
    """Test job queue"""
    queue = JobQueue(max_workers=2)
    queue.start()
    
    # Register handler
    def publish_handler(payload):
        print(f"Publishing: {payload}")
        return {"success": True, "listing_id": "123"}
    
    queue.register_handler("publish", publish_handler)
    
    # Enqueue job
    job_id = queue.enqueue(
        "publish",
        {"product_id": "test-123", "marketplace_id": "gumroad"},
        priority=JobPriority.HIGH
    )
    
    time.sleep(2)
    
    job = queue.get_job(job_id)
    print(f"Job: {job}")
    
    queue.stop()


if __name__ == "__main__":
    main()
