#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Queue Engine
Job queue with priority, scheduling, dead letter, and worker pools.
"""

import os
import sys
import json
import uuid
import logging
import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from queue import PriorityQueue, Empty
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.sales-automation.queue")


class JobState(Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    SCHEDULED = "scheduled"
    RETRYING = "retrying"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"


class JobPriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class QueueJob:
    job_id: str
    job_type: str
    priority: int
    state: str
    payload: Dict[str, Any]
    created_at: str
    scheduled_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout: int = 300
    worker_id: Optional[str] = None


class DeadLetterQueue:
    """Dead letter queue for permanently failed jobs"""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def enqueue(self, job: QueueJob):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO dead_letter_queue 
                (id, job_type, priority, payload, error_message, retry_count, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                job.job_id, job.job_type, job.priority,
                json.dumps(job.payload), job.error_message,
                job.retry_count, datetime.now().isoformat()
            ))
            conn.commit()
            logger.warning(f"Job moved to dead letter queue: {job.job_id}")
        except Exception as e:
            logger.error(f"Failed to enqueue dead letter: {e}")


class QueueEngine:
    """Main job queue with worker pools"""
    
    def __init__(self, db_manager, max_workers: int = 5):
        self.db = db_manager
        self._queue = PriorityQueue()
        self._jobs: Dict[str, QueueJob] = {}
        self._workers: List[threading.Thread] = []
        self._max_workers = max_workers
        self._running = False
        self._lock = threading.Lock()
        self._handlers: Dict[str, Callable] = {}
        self.dead_letter_queue = DeadLetterQueue(db_manager)
    
    def start(self):
        if self._running:
            return
        self._running = True
        for i in range(self._max_workers):
            worker = threading.Thread(target=self._worker_loop, args=(i,), daemon=True)
            worker.start()
            self._workers.append(worker)
        logger.info(f"Queue engine started with {self._max_workers} workers")
    
    def stop(self):
        self._running = False
        for worker in self._workers:
            worker.join(timeout=5)
        logger.info("Queue engine stopped")
    
    def enqueue(self, job_type: str, payload: Dict[str, Any],
                priority: JobPriority = JobPriority.NORMAL,
                max_retries: int = 3,
                timeout: int = 300,
                scheduled_at: Optional[str] = None) -> str:
        job_id = f"job-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        job = QueueJob(
            job_id=job_id,
            job_type=job_type,
            priority=priority.value,
            state=JobState.QUEUED.value,
            payload=payload,
            created_at=datetime.now().isoformat(),
            scheduled_at=scheduled_at,
            max_retries=max_retries,
            timeout=timeout
        )
        with self._lock:
            self._jobs[job_id] = job
            self._queue.put((priority.value, job.created_at, job_id))
        logger.info(f"Job enqueued: {job_id} ({job_type})")
        return job_id
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
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
        with self._lock:
            job = self._jobs.get(job_id)
            if job and job.state in [JobState.PENDING.value, JobState.QUEUED.value]:
                job.state = JobState.CANCELLED.value
                logger.info(f"Job cancelled: {job_id}")
                return True
        return False
    
    def register_handler(self, job_type: str, handler: Callable):
        self._handlers[job_type] = handler
    
    def _worker_loop(self, worker_id: int):
        while self._running:
            try:
                priority, created_at, job_id = self._queue.get(timeout=1)
                self._process_job(job_id, worker_id)
            except Empty:
                continue
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
    
    def _process_job(self, job_id: str, worker_id: int):
        job = self._jobs.get(job_id)
        if not job or job.state == JobState.CANCELLED.value:
            return
        
        job.state = JobState.RUNNING.value
        job.started_at = datetime.now().isoformat()
        job.worker_id = f"worker-{worker_id}"
        
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
                job.state = JobState.RETRYING.value
                logger.warning(f"Job retrying: {job_id} (attempt {job.retry_count})")
                time.sleep(2 ** job.retry_count)
                self._queue.put((job.priority, job.created_at, job_id))
            else:
                job.state = JobState.DEAD_LETTER.value
                self.dead_letter_queue.enqueue(job)
                logger.error(f"Job failed permanently: {job_id} - {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            states = {}
            for job in self._jobs.values():
                states[job.state] = states.get(job.state, 0) + 1
            return {
                "total_jobs": len(self._jobs),
                "states": states,
                "queue_size": self._queue.qsize(),
                "workers": self._max_workers
            }


def main():
    engine = QueueEngine(None, max_workers=2)
    print("Queue Engine initialized")


if __name__ == "__main__":
    main()
