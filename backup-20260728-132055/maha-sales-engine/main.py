#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Main Entry Point
Production-ready application startup with all modules.
"""

import os
import sys
import json
import time
import signal
import logging
import threading
import uvicorn
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from shared.core_engine import CoreEngine, get_engine
from shared.logging_utils import logging_manager, get_logger
from shared.health import health_monitor, get_health_monitor, DatabaseHealthChecker
from shared.database import DatabaseManager
from shared.auth import AuthManager
from shared.cache import CacheManager
from shared.utils import FileUtils, TimeUtils

logger = get_logger("main")


class Application:
    """Main application class"""
    
    def __init__(self):
        self.engine = None
        self.db = None
        self.cache = None
        self.auth = None
        self.running = False
        
    def initialize(self):
        """Initialize all components"""
        try:
            logger.info("=" * 60)
            logger.info("MAHA SALES ENGINE V1 - Starting Up")
            logger.info("=" * 60)
            
            # Initialize core engine
            self.engine = get_engine()
            logger.info("Core engine initialized")
            
            # Setup logging
            log_config = self.engine.config.get("logging", {})
            logging_manager.setup(log_config)
            logger.info("Logging system initialized")
            
            # Initialize database
            db_path = self.engine.config.get("database", {}).get("path", "data/maha.db")
            self.db = DatabaseManager(db_path)
            logger.info(f"Database initialized: {db_path}")
            
            # Initialize cache
            redis_url = os.environ.get("REDIS_URL")
            self.cache = CacheManager(redis_url)
            logger.info("Cache system initialized")
            
            # Initialize auth
            self.auth = AuthManager(self.db)
            logger.info("Authentication system initialized")
            
            # Register health checkers
            health_monitor.register_checker(DatabaseHealthChecker(self.db))
            if redis_url:
                from shared.health import RedisHealthChecker
                try:
                    import redis
                    redis_client = redis.from_url(redis_url)
                    health_monitor.register_checker(RedisHealthChecker(redis_client))
                except:
                    pass
            
            logger.info("Health monitoring initialized")
            
            # Register modules
            self.engine.register_module("database", self.db)
            self.engine.register_module("cache", self.cache)
            self.engine.register_module("auth", self.auth)
            
            logger.info("All modules registered")
            logger.info("=" * 60)
            logger.info("Initialization Complete - Ready to Start")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}", exc_info=True)
            return False
    
    def start(self):
        """Start the application"""
        if not self.initialize():
            logger.error("Failed to initialize application")
            sys.exit(1)
        
        self.running = True
        self.engine.start()
        
        # Start API servers
        self._start_apis()
    
    def _start_apis(self):
        """Start all API servers"""
        api_config = self.engine.config.get("api", {})
        host = api_config.get("host", "0.0.0.0")
        port = api_config.get("port", 8000)
        workers = api_config.get("workers", 1)
        
        logger.info(f"Starting API server on {host}:{port}")
        
        # Import and run API gateway
        try:
            from api.api_gateway import app as gateway_app
            uvicorn.run(
                gateway_app,
                host=host,
                port=port,
                log_level="info",
                access_log=True
            )
        except Exception as e:
            logger.error(f"Failed to start API gateway: {e}")
            sys.exit(1)
    
    def stop(self):
        """Stop the application gracefully"""
        logger.info("Shutting down application...")
        self.running = False
        
        if self.engine:
            self.engine.stop()
        
        if self.db:
            self.db.close()
        
        if self.cache:
            self.cache.close()
        
        logger.info("Application stopped")
        sys.exit(0)


def main():
    """Main entry point"""
    app = Application()
    
    # Setup signal handlers
    def handle_signal(signum, frame):
        logger.info(f"Received signal {signum}")
        app.stop()
    
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    # Start application
    app.start()


if __name__ == "__main__":
    main()
