#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Optimization Queue
Queue for optimization tasks with priority and retry logic.
"""

import os
import sys
import json
import time
import uuid
import logging
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from queue import Queue, Empty
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.optimization.queue")


class QueueStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class QueueItem:
    item_id: str
    optimization_id: str
    category: str
    priority: int
    payload: Dict[str, Any]
    status: QueueStatus
    retry_count: int = 0
    max_retries: int = 3
    error: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    processed_at: Optional[str] = None
    completed_at: Optional[str] = None


class OptimizationQueue:
    """
    Optimization queue with priority and retry logic.
    """
    
    def __init__(self, max_workers: int = 4):
        self._queue: Queue = Queue()
        self._max_workers = max_workers
        self._workers: List[threading.Thread] = []
        self._items: Dict[str, QueueItem] = {}
        self._lock = threading.Lock()
        self._running = False
    
    def enqueue(self, optimization_id: str, category: str, payload: Dict[str, Any], priority: int = 5) -> QueueItem:
        """Enqueue optimization task"""
        item_id = f"q-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
        
        item = QueueItem(
            item_id=item_id,
            optimization_id=optimization_id,
            category=category,
            priority=priority,
            payload=payload,
            status=QueueStatus.PENDING
        )
        
        with self._lock:
            self._items[item_id] = item
            self._queue.put((priority, item_id))
        
        logger.info(f"Item enqueued: {item_id} (priority={priority})")
        return item
    
    def dequeue(self) -> Optional[QueueItem]:
        """Dequeue highest priority item"""
        try:
            priority, item_id = self._queue.get(timeout=1)
            with self._lock:
                item = self._items.get(item_id)
                if item:
                    item.status = QueueStatus.PROCESSING
                    item.processed_at = datetime.now().isoformat()
                return item
        except Empty:
            return None
    
    def mark_completed(self, item_id: str):
        """Mark item as completed"""
        with self._lock:
            item = self._items.get(item_id)
            if item:
                item.status = QueueStatus.COMPLETED
                item.completed_at = datetime.now().isoformat()
    
    def mark_failed(self, item_id: str, error: str):
        """Mark item as failed and retry if possible"""
        with self._lock:
            item = self._items.get(item_id)
            if not item:
                return
            
            item.error = error
            item.retry_count += 1
            
            if item.retry_count < item.max_retries:
                item.status = QueueStatus.RETRYING
                self._queue.put((item.priority, item_id))
                logger.warning(f"Item retrying: {item_id} (attempt {item.retry_count})")
            else:
                item.status = QueueStatus.FAILED
                logger.error(f"Item failed permanently: {item_id}")
    
    def start(self):
        """Start queue workers"""
        self._running = True
        for i in range(self._max_workers):
            worker = threading.Thread(target=self._worker_loop, args=(i,), daemon=True)
            worker.start()
            self._workers.append(worker)
        logger.info(f"Queue started with {self._max_workers} workers")
    
    def stop(self):
        """Stop queue workers"""
        self._running = False
        for worker in self._workers:
            worker.join()
        logger.info("Queue stopped")
    
    def _worker_loop(self, worker_id: int):
        """Worker loop"""
        while self._running:
            item = self.dequeue()
            if item:
                try:
                    # Process item
                    logger.info(f"Worker {worker_id} processing: {item.item_id}")
                    # In production, execute optimization here
                    self.mark_completed(item.item_id)
                except Exception as e:
                    self.mark_failed(item.item_id, str(e))


def main():
    print("Optimization Queue loaded")


if __name__ == "__main__":
    main()
