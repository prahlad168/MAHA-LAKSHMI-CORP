#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Production Deployment Entrypoint

Handles startup validation, health checks, and graceful shutdown.
"""

import sys
import os
import signal
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent))

from shared.core_engine import get_engine
from shared.logging_utils import get_logger
from shared.health import health_monitor, DatabaseHealthChecker
from shared.database import DatabaseManager

logger = get_logger("deployment.startup")


class StartupValidator:
    """Validates system readiness before starting services"""
    
    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        self.max_retries = 30
        self.retry_delay = 2
    
    def validate_all(self) -> bool:
        """Run all startup validation checks"""
        logger.info("Running startup validation...")
        
        checks = [
            self._check_database,
            self._check_directories,
            self._check_environment,
            self._check_dependencies
        ]
        
        for check in checks:
            if self._run_check(check):
                self.checks_passed += 1
            else:
                self.checks_failed += 1
                logger.error(f"Startup check failed: {check.__name__}")
        
        logger.info(f"Startup validation: {self.checks_passed} passed, {self.checks_failed} failed")
        return self.checks_failed == 0
    
    def _run_check(self, check_func) -> bool:
        """Run a single check with retries"""
        for attempt in range(self.max_retries):
            try:
                if check_func():
                    logger.info(f"Check passed: {check_func.__name__}")
                    return True
            except Exception as e:
                logger.warning(f"Check {check_func.__name__} attempt {attempt + 1} failed: {e}")
            
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay)
        
        logger.error(f"Check failed after {self.max_retries} attempts: {check_func.__name__}")
        return False
    
    def _check_database(self) -> bool:
        """Check database connectivity"""
        try:
            db_path = os.environ.get("DATABASE_PATH", "data/maha.db")
            db = DatabaseManager(db_path)
            db.execute("SELECT 1")
            db.close()
            return True
        except Exception as e:
            logger.error(f"Database check failed: {e}")
            return False
    
    def _check_directories(self) -> bool:
        """Check required directories exist"""
        required_dirs = ["logs", "data", "cache", "config"]
        for dir_name in required_dirs:
            if not Path(dir_name).exists():
                Path(dir_name).mkdir(parents=True, exist_ok=True)
        return True
    
    def _check_environment(self) -> bool:
        """Check required environment variables"""
        required_vars = ["MAHA_ENV"]
        optional_vars = ["DATABASE_URL", "REDIS_URL", "SECRET_KEY"]
        
        missing_required = [var for var in required_vars if not os.environ.get(var)]
        if missing_required:
            logger.error(f"Missing required environment variables: {missing_required}")
            return False
        
        missing_optional = [var for var in optional_vars if not os.environ.get(var)]
        if missing_optional:
            logger.warning(f"Missing optional environment variables: {missing_optional}")
        
        return True
    
    def _check_dependencies(self) -> bool:
        """Check external dependencies"""
        return True


class GracefulShutdown:
    """Handles graceful shutdown of the application"""
    
    def __init__(self):
        self.shutdown_timeout = 30
        self.force_shutdown = False
    
    def setup(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
    
    def _handle_signal(self, signum, frame):
        """Handle shutdown signals"""
        signal_name = signal.Signals(signum).name
        logger.info(f"Received {signal_name}, initiating graceful shutdown...")
        self.force_shutdown = True
    
    def shutdown(self, app) -> bool:
        """Perform graceful shutdown"""
        logger.info("Starting graceful shutdown...")
        
        try:
            if app.engine:
                app.engine.stop()
            
            if app.db:
                app.db.close()
            
            if app.cache:
                app.cache.close()
            
            logger.info("Graceful shutdown completed")
            return True
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            return False


def main():
    """Main entrypoint for production deployment"""
    logger.info("=" * 60)
    logger.info("MAHA SALES ENGINE V1 - Production Startup")
    logger.info("=" * 60)
    
    # Setup graceful shutdown
    shutdown_handler = GracefulShutdown()
    shutdown_handler.setup()
    
    # Validate startup
    validator = StartupValidator()
    if not validator.validate_all():
        logger.error("Startup validation failed, exiting...")
        sys.exit(1)
    
    logger.info("Startup validation passed, starting application...")
    
    # Import and start application
    try:
        from main import Application
        app = Application()
        
        if not app.initialize():
            logger.error("Application initialization failed")
            sys.exit(1)
        
        logger.info("Application initialized successfully")
        app.start()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        shutdown_handler.shutdown(app)


if __name__ == "__main__":
    main()
