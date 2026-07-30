#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Deployment Scripts

Production deployment automation scripts.
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

logger = get_logger("deployment.scripts")


@dataclass
class DeploymentResult:
    """Deployment result"""
    success: bool
    message: str
    details: Dict[str, Any] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.details is None:
            self.details = {}


class DeploymentScripts:
    """Production deployment automation scripts"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.deploy_dir = base_dir / "deploy"
        self.logger = get_logger("deployment.scripts")
    
    def pre_deploy_checks(self) -> DeploymentResult:
        """Run pre-deployment checks"""
        checks = []
        all_passed = True
        
        # Check Docker
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                checks.append({"check": "docker", "status": "passed", "version": result.stdout.strip()})
            else:
                checks.append({"check": "docker", "status": "failed", "error": result.stderr})
                all_passed = False
        except Exception as e:
            checks.append({"check": "docker", "status": "failed", "error": str(e)})
            all_passed = False
        
        # Check Docker Compose
        try:
            result = subprocess.run(["docker-compose", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                checks.append({"check": "docker_compose", "status": "passed", "version": result.stdout.strip()})
            else:
                checks.append({"check": "docker_compose", "status": "failed", "error": result.stderr})
                all_passed = False
        except Exception as e:
            checks.append({"check": "docker_compose", "status": "failed", "error": str(e)})
            all_passed = False
        
        # Check required files
        required_files = ["Dockerfile", "docker-compose.yml", "requirements.txt", "config/engine.yaml"]
        for file_path in required_files:
            full_path = self.base_dir / file_path
            if full_path.exists():
                checks.append({"check": f"file_{file_path}", "status": "passed"})
            else:
                checks.append({"check": f"file_{file_path}", "status": "failed", "error": "File not found"})
                all_passed = False
        
        return DeploymentResult(
            success=all_passed,
            message="Pre-deployment checks completed",
            details={"checks": checks}
        )
    
    def build_images(self, services: Optional[List[str]] = None) -> DeploymentResult:
        """Build Docker images"""
        try:
            cmd = ["docker-compose", "build"]
            if services:
                cmd.extend(services)
            
            result = subprocess.run(
                cmd,
                cwd=self.base_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return DeploymentResult(
                    success=True,
                    message="Docker images built successfully",
                    details={"output": result.stdout}
                )
            else:
                return DeploymentResult(
                    success=False,
                    message="Docker build failed",
                    details={"error": result.stderr}
                )
        except Exception as e:
            return DeploymentResult(
                success=False,
                message=f"Build failed: {e}",
                details={"error": str(e)}
            )
    
    def deploy(self, services: Optional[List[str]] = None) -> DeploymentResult:
        """Deploy services"""
        try:
            cmd = ["docker-compose", "up", "-d"]
            if services:
                cmd.extend(services)
            
            result = subprocess.run(
                cmd,
                cwd=self.base_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return DeploymentResult(
                    success=True,
                    message="Deployment successful",
                    details={"output": result.stdout}
                )
            else:
                return DeploymentResult(
                    success=False,
                    message="Deployment failed",
                    details={"error": result.stderr}
                )
        except Exception as e:
            return DeploymentResult(
                success=False,
                message=f"Deployment failed: {e}",
                details={"error": str(e)}
            )
    
    def rollback(self, services: Optional[List[str]] = None) -> DeploymentResult:
        """Rollback deployment"""
        try:
            # Stop services
            cmd = ["docker-compose", "down"]
            if services:
                cmd.extend(services)
            
            result = subprocess.run(
                cmd,
                cwd=self.base_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return DeploymentResult(
                    success=True,
                    message="Rollback successful",
                    details={"output": result.stdout}
                )
            else:
                return DeploymentResult(
                    success=False,
                    message="Rollback failed",
                    details={"error": result.stderr}
                )
        except Exception as e:
            return DeploymentResult(
                success=False,
                message=f"Rollback failed: {e}",
                details={"error": str(e)}
            )
    
    def get_status(self) -> DeploymentResult:
        """Get deployment status"""
        try:
            result = subprocess.run(
                ["docker-compose", "ps"],
                cwd=self.base_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return DeploymentResult(
                    success=True,
                    message="Status retrieved",
                    details={"output": result.stdout}
                )
            else:
                return DeploymentResult(
                    success=False,
                    message="Failed to get status",
                    details={"error": result.stderr}
                )
        except Exception as e:
            return DeploymentResult(
                success=False,
                message=f"Status check failed: {e}",
                details={"error": str(e)}
            )
    
    def run_migrations(self) -> DeploymentResult:
        """Run database migrations"""
        try:
            migration_script = self.deploy_dir / "migrations" / "runner.py"
            result = subprocess.run(
                [sys.executable, str(migration_script)],
                cwd=self.base_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return DeploymentResult(
                    success=True,
                    message="Migrations completed",
                    details={"output": result.stdout}
                )
            else:
                return DeploymentResult(
                    success=False,
                    message="Migrations failed",
                    details={"error": result.stderr}
                )
        except Exception as e:
            return DeploymentResult(
                success=False,
                message=f"Migration failed: {e}",
                details={"error": str(e)}
            )
    
    def health_check(self) -> DeploymentResult:
        """Run health check"""
        try:
            health_script = self.deploy_dir / "health.py"
            result = subprocess.run(
                [sys.executable, str(health_script), "--check"],
                cwd=self.base_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                health_data = json.loads(result.stdout)
                return DeploymentResult(
                    success=health_data.get("status") == "healthy",
                    message="Health check completed",
                    details={"health": health_data}
                )
            else:
                return DeploymentResult(
                    success=False,
                    message="Health check failed",
                    details={"error": result.stderr}
                )
        except Exception as e:
            return DeploymentResult(
                success=False,
                message=f"Health check failed: {e}",
                details={"error": str(e)}
            )


def main():
    """CLI for deployment scripts"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deployment scripts")
    parser.add_argument("command", choices=["pre-check", "build", "deploy", "rollback", "status", "migrate", "health"])
    
    args = parser.parse_args()
    
    base_dir = Path(__file__).parent.parent
    scripts = DeploymentScripts(base_dir)
    
    if args.command == "pre-check":
        result = scripts.pre_deploy_checks()
    elif args.command == "build":
        result = scripts.build_images()
    elif args.command == "deploy":
        result = scripts.deploy()
    elif args.command == "rollback":
        result = scripts.rollback()
    elif args.command == "status":
        result = scripts.get_status()
    elif args.command == "migrate":
        result = scripts.run_migrations()
    elif args.command == "health":
        result = scripts.health_check()
    else:
        result = DeploymentResult(success=False, message="Unknown command")
    
    print(json.dumps(result.__dict__, indent=2, default=str))
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
