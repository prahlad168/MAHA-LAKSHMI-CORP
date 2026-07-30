#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Production Validation

Validates system readiness for production deployment.
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
from shared.core_engine import get_engine
from shared.database import DatabaseManager
from shared.health import health_monitor

logger = get_logger("deployment.validation")


@dataclass
class ValidationResult:
    """Validation check result"""
    check_name: str
    passed: bool
    message: str
    details: Dict[str, Any] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.details is None:
            self.details = {}


class ProductionValidator:
    """Validates production readiness"""
    
    def __init__(self):
        self.results: List[ValidationResult] = []
        self.logger = get_logger("deployment.validation")
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all production validation checks"""
        self.results = []
        
        checks = [
            self._check_environment,
            self._check_database,
            self._check_redis,
            self._check_docker,
            self._check_configuration,
            self._check_health_endpoints,
            self._check_security,
            self._check_dependencies,
            self._check_disk_space,
            self._check_ports
        ]
        
        for check in checks:
            try:
                result = check()
                self.results.append(result)
            except Exception as e:
                self.results.append(ValidationResult(
                    check_name=check.__name__,
                    passed=False,
                    message=str(e)
                ))
        
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        
        return {
            "valid": passed == total,
            "passed": passed,
            "total": total,
            "results": [r.__dict__ for r in self.results]
        }
    
    def _check_environment(self) -> ValidationResult:
        """Check environment variables"""
        required = ["MAHA_ENV"]
        optional = ["DATABASE_URL", "REDIS_URL", "SECRET_KEY"]
        
        missing_required = [var for var in required if not os.environ.get(var)]
        missing_optional = [var for var in optional if not os.environ.get(var)]
        
        if missing_required:
            return ValidationResult(
                check_name="environment",
                passed=False,
                message=f"Missing required environment variables: {missing_required}"
            )
        
        message = "Environment OK"
        if missing_optional:
            message += f" (optional vars missing: {missing_optional})"
        
        return ValidationResult(
            check_name="environment",
            passed=True,
            message=message,
            details={
                "required": required,
                "optional": optional,
                "missing_optional": missing_optional
            }
        )
    
    def _check_database(self) -> ValidationResult:
        """Check database connectivity"""
        try:
            db_path = os.environ.get("DATABASE_PATH", "data/maha.db")
            db = DatabaseManager(db_path)
            result = db.execute("SELECT 1")
            db.close()
            
            if result and result[0].get("1") == 1:
                return ValidationResult(
                    check_name="database",
                    passed=True,
                    message="Database connection OK"
                )
            else:
                return ValidationResult(
                    check_name="database",
                    passed=False,
                    message="Database query returned unexpected result"
                )
        except Exception as e:
            return ValidationResult(
                check_name="database",
                passed=False,
                message=f"Database check failed: {e}"
            )
    
    def _check_redis(self) -> ValidationResult:
        """Check Redis connectivity"""
        try:
            redis_url = os.environ.get("REDIS_URL")
            if not redis_url:
                return ValidationResult(
                    check_name="redis",
                    passed=True,
                    message="Redis not configured (optional)"
                )
            
            import redis
            client = redis.from_url(redis_url)
            client.ping()
            client.close()
            
            return ValidationResult(
                check_name="redis",
                passed=True,
                message="Redis connection OK"
            )
        except ImportError:
            return ValidationResult(
                check_name="redis",
                passed=True,
                message="Redis not installed (optional)"
            )
        except Exception as e:
            return ValidationResult(
                check_name="redis",
                passed=False,
                message=f"Redis check failed: {e}"
            )
    
    def _check_docker(self) -> ValidationResult:
        """Check Docker availability"""
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                return ValidationResult(
                    check_name="docker",
                    passed=True,
                    message=f"Docker available: {result.stdout.strip()}"
                )
            else:
                return ValidationResult(
                    check_name="docker",
                    passed=False,
                    message="Docker not available"
                )
        except Exception as e:
            return ValidationResult(
                check_name="docker",
                passed=False,
                message=f"Docker check failed: {e}"
            )
    
    def _check_configuration(self) -> ValidationResult:
        """Check configuration files"""
        try:
            config_path = os.environ.get("MAHA_CONFIG_PATH", "config/engine.yaml")
            if not Path(config_path).exists():
                return ValidationResult(
                    check_name="configuration",
                    passed=False,
                    message=f"Config file not found: {config_path}"
                )
            
            import yaml
            with open(config_path) as f:
                config = yaml.safe_load(f)
            
            required_sections = ["engine", "database", "logging"]
            missing = [s for s in required_sections if s not in config]
            
            if missing:
                return ValidationResult(
                    check_name="configuration",
                    passed=False,
                    message=f"Missing config sections: {missing}"
                )
            
            return ValidationResult(
                check_name="configuration",
                passed=True,
                message="Configuration OK",
                details={"sections": list(config.keys())}
            )
        except Exception as e:
            return ValidationResult(
                check_name="configuration",
                passed=False,
                message=f"Configuration check failed: {e}"
            )
    
    def _check_health_endpoints(self) -> ValidationResult:
        """Check health endpoints"""
        try:
            engine = get_engine()
            health = engine.get_health()
            
            if health.get("status") == "running":
                return ValidationResult(
                    check_name="health_endpoints",
                    passed=True,
                    message="Health endpoints OK"
                )
            else:
                return ValidationResult(
                    check_name="health_endpoints",
                    passed=False,
                    message=f"Engine not running: {health.get('status')}"
                )
        except Exception as e:
            return ValidationResult(
                check_name="health_endpoints",
                passed=False,
                message=f"Health check failed: {e}"
            )
    
    def _check_security(self) -> ValidationResult:
        """Check security configuration"""
        try:
            secret_key = os.environ.get("MAHA_SECRET_KEY")
            if not secret_key:
                return ValidationResult(
                    check_name="security",
                    passed=False,
                    message="MAHA_SECRET_KEY not set"
                )
            
            if secret_key == "change-me-in-production-use-strong-secret":
                return ValidationResult(
                    check_name="security",
                    passed=False,
                    message="Using default secret key"
                )
            
            return ValidationResult(
                check_name="security",
                passed=True,
                message="Security configuration OK"
            )
        except Exception as e:
            return ValidationResult(
                check_name="security",
                passed=False,
                message=f"Security check failed: {e}"
            )
    
    def _check_dependencies(self) -> ValidationResult:
        """Check Python dependencies"""
        try:
            result = subprocess.run(
                ["python", "-c", "import sys; print(sys.version)"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return ValidationResult(
                    check_name="dependencies",
                    passed=True,
                    message=f"Python OK: {result.stdout.strip()}"
                )
            else:
                return ValidationResult(
                    check_name="dependencies",
                    passed=False,
                    message="Python check failed"
                )
        except Exception as e:
            return ValidationResult(
                check_name="dependencies",
                passed=False,
                message=f"Dependency check failed: {e}"
            )
    
    def _check_disk_space(self) -> ValidationResult:
        """Check disk space"""
        try:
            import shutil
            usage = shutil.disk_usage(".")
            free_gb = usage.free / (1024**3)
            
            if free_gb < 5:
                return ValidationResult(
                    check_name="disk_space",
                    passed=False,
                    message=f"Low disk space: {free_gb:.2f} GB free"
                )
            
            return ValidationResult(
                check_name="disk_space",
                passed=True,
                message=f"Disk OK: {free_gb:.2f} GB free",
                details={"free_gb": round(free_gb, 2)}
            )
        except Exception as e:
            return ValidationResult(
                check_name="disk_space",
                passed=False,
                message=f"Disk check failed: {e}"
            )
    
    def _check_ports(self) -> ValidationResult:
        """Check required ports"""
        required_ports = [8000, 8001, 8002, 8003, 8004, 8005, 8006]
        available = []
        unavailable = []
        
        for port in required_ports:
            if self._is_port_available(port):
                available.append(port)
            else:
                unavailable.append(port)
        
        if unavailable:
            return ValidationResult(
                check_name="ports",
                passed=False,
                message=f"Ports in use: {unavailable}",
                details={"available": available, "unavailable": unavailable}
            )
        
        return ValidationResult(
            check_name="ports",
            passed=True,
            message="All required ports available",
            details={"available": available}
        )
    
    def _is_port_available(self, port: int) -> bool:
        """Check if port is available"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0
    
    def generate_report(self) -> str:
        """Generate validation report"""
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        
        report = []
        report.append("=" * 60)
        report.append("MAHA SALES ENGINE V1 - Production Validation Report")
        report.append("=" * 60)
        report.append(f"Timestamp: {datetime.now().isoformat()}")
        report.append(f"Result: {passed}/{total} checks passed")
        report.append("")
        
        for result in self.results:
            status = "PASS" if result.passed else "FAIL"
            report.append(f"[{status}] {result.check_name}: {result.message}")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)


def main():
    """CLI for production validator"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Production validation")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    validator = ProductionValidator()
    result = validator.run_all_checks()
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(validator.generate_report())
    
    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
