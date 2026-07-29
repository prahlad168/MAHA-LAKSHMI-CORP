#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Scheduler
Schedules optimization tasks.
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
from datetime import datetime, timedelta
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.optimization.scheduler")


class ScheduleStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ScheduledTask:
    task_id: str
    name: str
    func: Callable
    args: tuple
    kwargs: dict
    scheduled_at: str
    status: ScheduleStatus
    result: Any = None
    error: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class Scheduler:
    """
    Scheduler for optimization tasks.
    """
    
    def __init__(self):
        self._tasks: Dict[str, ScheduledTask] = {}
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None
    
    def schedule(self, name: str, func: Callable, args: tuple = (), kwargs: dict = None, run_at: datetime = None) -> ScheduledTask:
        """Schedule task"""
        if kwargs is None:
            kwargs = {}
        
        task_id = f"sched-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
        
        if run_at is None:
            run_at = datetime.now() + timedelta(minutes=5)
        
        task = ScheduledTask(
            task_id=task_id,
            name=name,
            func=func,
            args=args,
            kwargs=kwargs,
            scheduled_at=run_at.isoformat(),
            status=ScheduleStatus.PENDING
        )
        
        with self._lock:
            self._tasks[task_id] = task
        
        logger.info(f"Task scheduled: {task_id} - {name}")
        return task
    
    def run_pending(self):
        """Run pending tasks"""
        now = datetime.now()
        
        with self._lock:
            for task in list(self._tasks.values()):
                if task.status != ScheduleStatus.PENDING:
                    continue
                
                scheduled_at = datetime.fromisoformat(task.scheduled_at)
                if now < scheduled_at:
                    continue
                
                task.status = ScheduleStatus.RUNNING
                try:
                    task.result = task.func(*task.args, **task.kwargs)
                    task.status = ScheduleStatus.COMPLETED
                except Exception as e:
                    task.status = ScheduleStatus.FAILED
                    task.error = str(e)
                    logger.error(f"Task failed: {task.task_id} - {e}")
    
    def start(self):
        """Start scheduler"""
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("Scheduler started")
    
    def stop(self):
        """Stop scheduler"""
        self._running = False
        if self._thread:
            self._thread.join()
        logger.info("Scheduler stopped")
    
    def _run_loop(self):
        """Scheduler loop"""
        while self._running:
            self.run_pending()
            time.sleep(1)


def main():
    print("Scheduler loaded")


if __name__ == "__main__":
    main()
