#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Rollback Strategy

Production rollback mechanisms and procedures.
"""

import sys
import os
import json
import time
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.logging_utils import get_logger

logger = get_logger("deployment.rollback")


@dataclass
class RollbackPlan:
    """Rollback plan definition"""
    version: str
    timestamp: str
    steps: List[Dict[str, Any]]
    estimated_time: int
    rollback_type: str  # full, partial, database


class RollbackManager:
    """Manages production rollbacks"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.rollback_dir = base_dir / "deploy" / "rollback"
        self.rollback_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger("deployment.rollback")
    
    def create_rollback_plan(self, current_version: str) -> RollbackPlan:
        """Create rollback plan"""
        timestamp = datetime.now().isoformat()
        
        steps = [
            {
                "step": 1,
                "name": "stop_services",
                "description": "Stop all running services",
                "command": "docker-compose -f docker-compose.prod.yml down",
                "timeout": 60
            },
            {
                "step": 2,
                "name": "backup_current",
                "description": "Backup current database and data",
                "command": "python deploy/scripts/backup.py",
                "timeout": 300
            },
            {
                "step": 3,
                "name": "restore_previous",
                "description": "Restore previous version",
                "command": f"git checkout {current_version}",
                "timeout": 120
            },
            {
                "step": 4,
                "name": "run_migrations",
                "description": "Run database migrations",
                "command": "python deploy/migrations/runner.py",
                "timeout": 120
            },
            {
                "step": 5,
                "name": "redeploy",
                "description": "Redeploy services",
                "command": "bash deploy/scripts/deploy.sh production",
                "timeout": 300
            },
            {
                "step": 6,
                "name": "health_check",
                "description": "Verify health after rollback",
                "command": "python deploy/health.py --check",
                "timeout": 60
            }
        ]
        
        return RollbackPlan(
            version=current_version,
            timestamp=timestamp,
            steps=steps,
            estimated_time=sum(step["timeout"] for step in steps),
            rollback_type="full"
        )
    
    def execute_rollback(self, plan: RollbackPlan) -> Dict[str, Any]:
        """Execute rollback plan"""
        logger.info(f"Starting rollback to {plan.version}")
        
        results = []
        failed_steps = []
        
        for step in plan.steps:
            logger.info(f"Executing step {step['step']}: {step['name']}")
            
            try:
                result = self._execute_step(step)
                results.append({
                    "step": step["step"],
                    "name": step["name"],
                    "success": result["success"],
                    "output": result.get("output", ""),
                    "error": result.get("error", "")
                })
                
                if not result["success"]:
                    failed_steps.append(step["name"])
                    logger.error(f"Step failed: {step['name']}")
                    
                    # Stop rollback on critical failure
                    if step["name"] in ["stop_services", "restore_previous"]:
                        logger.error("Critical step failed, aborting rollback")
                        break
            except Exception as e:
                logger.error(f"Step error: {step['name']} - {e}")
                results.append({
                    "step": step["step"],
                    "name": step["name"],
                    "success": False,
                    "error": str(e)
                })
                failed_steps.append(step["name"])
        
        # Save rollback report
        report = {
            "plan": plan.__dict__,
            "results": results,
            "failed_steps": failed_steps,
            "completed_at": datetime.now().isoformat()
        }
        
        report_path = self.rollback_dir / f"rollback-{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        success = len(failed_steps) == 0
        logger.info(f"Rollback completed: {'success' if success else 'failed'}")
        
        return {
            "success": success,
            "failed_steps": failed_steps,
            "report_path": str(report_path)
        }
    
    def _execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single rollback step"""
        try:
            result = subprocess.run(
                step["command"],
                shell=True,
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=step.get("timeout", 300)
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else ""
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": f"Command timed out after {step.get('timeout', 300)}s"
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e)
            }
    
    def get_rollback_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get rollback history"""
        reports = []
        for report_file in sorted(self.rollback_dir.glob("rollback-*.json"), reverse=True)[:limit]:
            try:
                with open(report_file) as f:
                    reports.append(json.load(f))
            except Exception as e:
                logger.error(f"Failed to read rollback report {report_file}: {e}")
        return reports
    
    def quick_rollback(self) -> Dict[str, Any]:
        """Quick rollback using previous docker-compose config"""
        plan = self.create_rollback_plan("previous")
        return self.execute_rollback(plan)


def main():
    """CLI for rollback manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Rollback manager")
    parser.add_argument("command", choices=["create", "execute", "history", "quick"])
    parser.add_argument("--version", help="Version to rollback to")
    parser.add_argument("--base-dir", default=".", help="Base directory")
    
    args = parser.parse_args()
    
    base_dir = Path(args.base_dir).resolve()
    manager = RollbackManager(base_dir)
    
    if args.command == "create":
        if not args.version:
            print("Error: --version required for create command")
            sys.exit(1)
        plan = manager.create_rollback_plan(args.version)
        print(json.dumps(plan.__dict__, indent=2, default=str))
    
    elif args.command == "execute":
        if not args.version:
            print("Error: --version required for execute command")
            sys.exit(1)
        plan = manager.create_rollback_plan(args.version)
        result = manager.execute_rollback(plan)
        print(json.dumps(result, indent=2, default=str))
        sys.exit(0 if result["success"] else 1)
    
    elif args.command == "history":
        history = manager.get_rollback_history()
        print(json.dumps(history, indent=2, default=str))
    
    elif args.command == "quick":
        result = manager.quick_rollback()
        print(json.dumps(result, indent=2, default=str))
        sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
