#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Scheduler
Responsibilities:
- Run jobs
- Retry failures
- Queue execution
- Background processing
- 24/7 operation
"""

import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from enum import Enum
import queue

logger = logging.getLogger("maha-sales-engine.scheduler")


class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class Job:
    """Scheduled job definition"""
    job_id: str
    name: str
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    interval_seconds: int = 3600
    max_retries: int = 3
    retry_delay: int = 60
    priority: int = 5
    enabled: bool = True
    last_run: Optional[str] = None
    next_run: Optional[str] = None
    run_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    status: JobStatus = JobStatus.PENDING


class Scheduler:
    """Job scheduler with retry and queue management"""
    
    def __init__(self):
        self.jobs: Dict[str, Job] = {}
        self.job_queue = queue.PriorityQueue()
        self.running = False
        self.worker_threads = []
        self.num_workers = 4
        self.lock = threading.Lock()
    
    def register_job(self, job: Job):
        """Register a new job"""
        with self.lock:
            self.jobs[job.job_id] = job
            self._schedule_job(job)
        logger.info(f"Job registered: {job.job_id} - {job.name}")
    
    def _schedule_job(self, job: Job):
        """Schedule job for execution"""
        if not job.enabled:
            return
        
        now = datetime.now()
        if job.next_run:
            next_run = datetime.fromisoformat(job.next_run)
            if next_run > now:
                self.job_queue.put((job.priority, next_run.timestamp(), job.job_id))
            else:
                self.job_queue.put((job.priority, now.timestamp(), job.job_id))
        else:
            self.job_queue.put((job.priority, now.timestamp(), job.job_id))
    
    def start(self):
        """Start scheduler"""
        if self.running:
            return
        
        self.running = True
        logger.info(f"Starting scheduler with {self.num_workers} workers")
        
        # Start worker threads
        for i in range(self.num_workers):
            t = threading.Thread(target=self._worker, daemon=True)
            t.start()
            self.worker_threads.append(t)
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
    
    def stop(self):
        """Stop scheduler"""
        self.running = False
        logger.info("Scheduler stopped")
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.running:
            try:
                self._check_and_schedule_jobs()
                time.sleep(10)
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(60)
    
    def _check_and_schedule_jobs(self):
        """Check jobs and schedule them"""
        with self.lock:
            now = datetime.now()
            for job in self.jobs.values():
                if not job.enabled:
                    continue
                
                last_run = datetime.fromisoformat(job.last_run) if job.last_run else None
                if last_run is None or (now - last_run).total_seconds() >= job.interval_seconds:
                    self._schedule_job(job)
    
    def _worker(self):
        """Worker thread for executing jobs"""
        while self.running:
            try:
                # Get job from queue with timeout
                priority, timestamp, job_id = self.job_queue.get(timeout=5)
                
                with self.lock:
                    if job_id not in self.jobs:
                        self.job_queue.task_done()
                        continue
                    
                    job = self.jobs[job_id]
                    
                    if not job.enabled:
                        self.job_queue.task_done()
                        continue
                    
                    # Execute job
                    self._execute_job(job)
                
                self.job_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Worker error: {e}")
                time.sleep(5)
    
    def _execute_job(self, job: Job):
        """Execute a job with retry logic"""
        job.status = JobStatus.RUNNING
        job.run_count += 1
        job.last_run = datetime.now().isoformat()
        
        logger.info(f"Executing job: {job.job_id} - {job.name}")
        
        for attempt in range(job.max_retries):
            try:
                result = job.func(*job.args, **job.kwargs)
                
                job.status = JobStatus.COMPLETED
                job.success_count += 1
                job.next_run = (datetime.now() + timedelta(seconds=job.interval_seconds)).isoformat()
                
                logger.info(f"Job completed: {job.job_id} (attempt {attempt + 1})")
                return result
                
            except Exception as e:
                job.failure_count += 1
                logger.warning(f"Job failed: {job.job_id} (attempt {attempt + 1}): {e}")
                
                if attempt < job.max_retries - 1:
                    job.status = JobStatus.RETRYING
                    time.sleep(job.retry_delay)
                else:
                    job.status = JobStatus.FAILED
                    logger.error(f"Job failed permanently: {job.job_id}")
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status"""
        with self.lock:
            if job_id not in self.jobs:
                return None
            
            job = self.jobs[job_id]
            return {
                "job_id": job.job_id,
                "name": job.name,
                "status": job.status.value,
                "last_run": job.last_run,
                "next_run": job.next_run,
                "run_count": job.run_count,
                "success_count": job.success_count,
                "failure_count": job.failure_count,
                "enabled": job.enabled
            }
    
    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """Get all jobs"""
        with self.lock:
            return [self.get_job_status(job_id) for job_id in self.jobs.keys()]
    
    def enable_job(self, job_id: str):
        """Enable a job"""
        with self.lock:
            if job_id in self.jobs:
                self.jobs[job_id].enabled = True
                self._schedule_job(self.jobs[job_id])
    
    def disable_job(self, job_id: str):
        """Disable a job"""
        with self.lock:
            if job_id in self.jobs:
                self.jobs[job_id].enabled = False
    
    def run_job_now(self, job_id: str):
        """Run a job immediately"""
        with self.lock:
            if job_id in self.jobs:
                job = self.jobs[job_id]
                self.job_queue.put((job.priority, datetime.now().timestamp(), job_id))


# ============ PREDEFINED JOBS ============

def create_daily_outreach_job(sales_agent) -> Job:
    """Create daily outreach job"""
    def run_outreach():
        sales_agent.run_daily_outreach()
    
    return Job(
        job_id="daily-outreach",
        name="Daily Outreach",
        func=run_outreach,
        interval_seconds=3600,  # Every hour
        max_retries=3,
        retry_delay=300,
        priority=3
    )


def create_daily_report_job(reporter) -> Job:
    """Create daily report job"""
    def run_report():
        reporter.send_daily_report()
    
    return Job(
        job_id="daily-report",
        name="Daily Report",
        func=run_report,
        interval_seconds=86400,  # Every 24 hours
        max_retries=2,
        retry_delay=600,
        priority=5
    )


def create_heartbeat_job(reporter) -> Job:
    """Create heartbeat job"""
    def send_heartbeat():
        reporter.send_heartbeat()
    
    return Job(
        job_id="heartbeat",
        name="Heartbeat",
        func=send_heartbeat,
        interval_seconds=60,  # Every minute
        max_retries=3,
        retry_delay=30,
        priority=1
    )


def create_market_research_job(market_analyzer) -> Job:
    """Create market research job"""
    def run_research():
        market_analyzer.analyze_digital_product_trends()
        market_analyzer.optimize_templates()
        market_analyzer.optimize_targeting()
    
    return Job(
        job_id="market-research",
        name="Market Research",
        func=run_research,
        interval_seconds=86400,  # Every 24 hours
        max_retries=2,
        retry_delay=600,
        priority=4
    )


def create_followup_job(sales_agent) -> Job:
    """Create follow-up job"""
    def run_followup():
        sales_agent.run_followup_sequence()
    
    return Job(
        job_id="followup-sequence",
        name="Follow-up Sequence",
        func=run_followup,
        interval_seconds=3600,  # Every hour
        max_retries=3,
        retry_delay=300,
        priority=2
    )


def create_backup_job(db_manager) -> Job:
    """Create database backup job"""
    def run_backup():
        db_manager.backup()
    
    return Job(
        job_id="database-backup",
        name="Database Backup",
        func=run_backup,
        interval_seconds=86400,  # Every 24 hours
        max_retries=2,
        retry_delay=300,
        priority=5
    )
