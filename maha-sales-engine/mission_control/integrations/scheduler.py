#!/usr/bin/env python3
"""
MAHA Sales Engine V1 - Mission Control Scheduler Integration

Integrates Mission Control with the existing Scheduler module.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.logging_utils import get_logger
from mission_control.models import MissionContext, MissionStatus

logger = get_logger("maha-sales-engine.mission-control.scheduler")


class SchedulerIntegration:
    """
    Integrates Mission Control with the Scheduler module.
    
    Registers mission control jobs with the existing scheduler
    and provides mission-aware scheduling capabilities.
    """
    
    def __init__(self, scheduler=None):
        """
        Initialize scheduler integration.
        
        Args:
            scheduler: Optional scheduler instance
        """
        self.scheduler = scheduler
        self._registered_jobs: Dict[str, str] = {}
        self.logger = get_logger("maha-sales-engine.mission-control.scheduler")
    
    def register_mission_jobs(self, mission_controller) -> Dict[str, str]:
        """
        Register mission control jobs with the scheduler.
        
        Args:
            mission_controller: Mission controller instance
            
        Returns:
            Dictionary of job IDs mapped to mission control operations
        """
        if not self.scheduler:
            self.logger.warning("Scheduler not available, skipping job registration")
            return {}
        
        try:
            from scheduler.scheduler import Job
            
            jobs = {
                "mission-health-check": Job(
                    job_id="mission-health-check",
                    name="Mission Control Health Check",
                    func=self._run_health_check,
                    args=(mission_controller,),
                    interval_seconds=60,
                    max_retries=2,
                    retry_delay=30,
                    priority=1
                ),
                "mission-metrics-aggregation": Job(
                    job_id="mission-metrics-aggregation",
                    name="Mission Metrics Aggregation",
                    func=self._run_metrics_aggregation,
                    args=(mission_controller,),
                    interval_seconds=300,
                    max_retries=3,
                    retry_delay=60,
                    priority=2
                ),
                "mission-alert-dispatch": Job(
                    job_id="mission-alert-dispatch",
                    name="Mission Alert Dispatch",
                    func=self._run_alert_dispatch,
                    args=(mission_controller,),
                    interval_seconds=30,
                    max_retries=2,
                    retry_delay=15,
                    priority=1
                )
            }
            
            for job_id, job in jobs.items():
                self.scheduler.register_job(job)
                self._registered_jobs[job_id] = job.job_id
                self.logger.info(f"Registered mission control job: {job_id}")
            
            return self._registered_jobs
        except Exception as e:
            self.logger.error(f"Failed to register mission jobs: {e}")
            return {}
    
    def _run_health_check(self, mission_controller) -> Dict[str, Any]:
        """Run health check job"""
        try:
            health = mission_controller.get_system_health()
            self.logger.debug(f"Health check completed: {health.get('status', 'unknown')}")
            return health
        except Exception as e:
            self.logger.error(f"Health check job failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def _run_metrics_aggregation(self, mission_controller) -> Dict[str, Any]:
        """Run metrics aggregation job"""
        try:
            metrics = mission_controller.get_controller_metrics()
            self.logger.debug(f"Metrics aggregation completed: {metrics}")
            return metrics
        except Exception as e:
            self.logger.error(f"Metrics aggregation job failed: {e}")
            return {"error": str(e)}
    
    def _run_alert_dispatch(self, mission_controller) -> Dict[str, Any]:
        """Run alert dispatch job"""
        try:
            from mission_control.repositories.mission_repository import MissionRepository
            repo = MissionRepository(mission_controller.db)
            pending_alerts = repo.list_pending_alerts(limit=100)
            
            dispatched = 0
            for alert in pending_alerts:
                if self._dispatch_alert(alert):
                    dispatched += 1
            
            self.logger.debug(f"Alert dispatch completed: {dispatched} alerts dispatched")
            return {"dispatched": dispatched}
        except Exception as e:
            self.logger.error(f"Alert dispatch job failed: {e}")
            return {"error": str(e)}
    
    def _dispatch_alert(self, alert) -> bool:
        """Dispatch single alert"""
        try:
            from mission_control.integrations.alerts import AlertDispatcher
            dispatcher = AlertDispatcher()
            return dispatcher.dispatch(alert)
        except Exception as e:
            self.logger.error(f"Failed to dispatch alert {alert.alert_id}: {e}")
            return False
    
    def get_registered_jobs(self) -> Dict[str, str]:
        """Get registered job IDs"""
        return dict(self._registered_jobs)
    
    def unregister_all_jobs(self) -> None:
        """Unregister all mission control jobs"""
        if not self.scheduler:
            return
        
        try:
            for job_id in list(self._registered_jobs.keys()):
                self.scheduler.disable_job(job_id)
                self.logger.info(f"Unregistered job: {job_id}")
            self._registered_jobs.clear()
        except Exception as e:
            self.logger.error(f"Failed to unregister jobs: {e}")
