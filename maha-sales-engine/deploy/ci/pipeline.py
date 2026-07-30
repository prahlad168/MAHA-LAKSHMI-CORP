#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - CI/CD Pipeline

Continuous Integration and Deployment pipeline.
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

logger = get_logger("deployment.cicd")


@dataclass
class PipelineStage:
    """CI/CD pipeline stage"""
    name: str
    status: str = "pending"
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    output: str = ""
    error: str = ""


class CIPipeline:
    """Continuous Integration pipeline"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.stages: List[PipelineStage] = []
    
    def run(self) -> Dict[str, Any]:
        """Run CI pipeline"""
        logger.info("Starting CI pipeline...")
        
        self.stages = [
            PipelineStage(name="lint"),
            PipelineStage(name="typecheck"),
            PipelineStage(name="test"),
            PipelineStage(name="security_scan")
        ]
        
        results = []
        for stage in self.stages:
            result = self._run_stage(stage)
            results.append(result)
            if not result.get("success", False):
                logger.error(f"CI stage failed: {stage.name}")
                return {
                    "success": False,
                    "failed_stage": stage.name,
                    "results": results
                }
        
        return {
            "success": True,
            "results": results
        }
    
    def _run_stage(self, stage: PipelineStage) -> Dict[str, Any]:
        """Run a single CI stage"""
        stage.status = "running"
        stage.started_at = datetime.now().isoformat()
        
        try:
            if stage.name == "lint":
                result = self._run_lint()
            elif stage.name == "typecheck":
                result = self._run_typecheck()
            elif stage.name == "test":
                result = self._run_tests()
            elif stage.name == "security_scan":
                result = self._run_security_scan()
            else:
                result = {"success": False, "error": "Unknown stage"}
            
            stage.status = "completed" if result.get("success") else "failed"
            stage.completed_at = datetime.now().isoformat()
            stage.output = result.get("output", "")
            stage.error = result.get("error", "")
            
            return result
        except Exception as e:
            stage.status = "failed"
            stage.completed_at = datetime.now().isoformat()
            stage.error = str(e)
            return {"success": False, "error": str(e)}
    
    def _run_lint(self) -> Dict[str, Any]:
        """Run linting"""
        try:
            result = subprocess.run(
                ["python", "-m", "ruff", "check", "."],
                cwd=self.base_dir,
                capture_output=True,
                text=True
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _run_typecheck(self) -> Dict[str, Any]:
        """Run type checking"""
        try:
            result = subprocess.run(
                ["python", "-m", "mypy", "."],
                cwd=self.base_dir,
                capture_output=True,
                text=True
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _run_tests(self) -> Dict[str, Any]:
        """Run tests"""
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-v"],
                cwd=self.base_dir,
                capture_output=True,
                text=True
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _run_security_scan(self) -> Dict[str, Any]:
        """Run security scan"""
        try:
            result = subprocess.run(
                ["python", "-m", "bandit", "-r", "."],
                cwd=self.base_dir,
                capture_output=True,
                text=True
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class CDPipeline:
    """Continuous Deployment pipeline"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.logger = get_logger("deployment.cicd")
    
    def deploy(self, environment: str = "production") -> Dict[str, Any]:
        """Deploy to environment"""
        logger.info(f"Starting CD pipeline for {environment}...")
        
        stages = [
            ("pre_deploy", self._pre_deploy),
            ("build", self._build),
            ("test", self._test_deployment),
            ("deploy", lambda: self._deploy(environment)),
            ("health_check", self._health_check)
        ]
        
        results = []
        for stage_name, stage_func in stages:
            logger.info(f"Running stage: {stage_name}")
            try:
                result = stage_func()
                results.append({
                    "stage": stage_name,
                    "success": result.get("success", False),
                    "details": result
                })
                if not result.get("success", False):
                    logger.error(f"CD stage failed: {stage_name}")
                    self._rollback()
                    return {
                        "success": False,
                        "failed_stage": stage_name,
                        "results": results
                    }
            except Exception as e:
                logger.error(f"CD stage error: {stage_name} - {e}")
                self._rollback()
                return {
                    "success": False,
                    "failed_stage": stage_name,
                    "error": str(e),
                    "results": results
                }
        
        return {
            "success": True,
            "environment": environment,
            "results": results
        }
    
    def _pre_deploy(self) -> Dict[str, Any]:
        """Pre-deployment checks"""
        scripts = DeploymentScripts(self.base_dir)
        return scripts.pre_deploy_checks().__dict__
    
    def _build(self) -> Dict[str, Any]:
        """Build deployment artifacts"""
        scripts = DeploymentScripts(self.base_dir)
        return scripts.build_images().__dict__
    
    def _test_deployment(self) -> Dict[str, Any]:
        """Test deployment"""
        scripts = DeploymentScripts(self.base_dir)
        return scripts.run_migrations().__dict__
    
    def _deploy(self, environment: str) -> Dict[str, Any]:
        """Deploy to environment"""
        scripts = DeploymentScripts(self.base_dir)
        return scripts.deploy().__dict__
    
    def _health_check(self) -> Dict[str, Any]:
        """Post-deployment health check"""
        scripts = DeploymentScripts(self.base_dir)
        return scripts.health_check().__dict__
    
    def _rollback(self) -> Dict[str, Any]:
        """Rollback deployment"""
        logger.info("Rolling back deployment...")
        scripts = DeploymentScripts(self.base_dir)
        return scripts.rollback().__dict__


def main():
    """CLI for CI/CD pipeline"""
    import argparse
    
    parser = argparse.ArgumentParser(description="CI/CD Pipeline")
    parser.add_argument("mode", choices=["ci", "cd"])
    parser.add_argument("--environment", default="production", help="Target environment")
    
    args = parser.parse_args()
    
    base_dir = Path(__file__).parent.parent
    
    if args.mode == "ci":
        pipeline = CIPipeline(base_dir)
        result = pipeline.run()
    else:
        pipeline = CDPipeline(base_dir)
        result = pipeline.deploy(args.environment)
    
    print(json.dumps(result, indent=2, default=str))
    sys.exit(0 if result.get("success", False) else 1)


if __name__ == "__main__":
    main()
