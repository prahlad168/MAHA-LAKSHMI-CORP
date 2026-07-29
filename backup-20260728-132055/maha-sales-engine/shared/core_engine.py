#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Core Engine
Production-ready core engine with dependency injection, logging, and health monitoring.
"""

import os
import sys
import json
import time
import signal
import logging
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.core")


class EngineStatus(Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class ModuleInfo:
    name: str
    instance: Any
    status: str
    initialized_at: Optional[str]
    error_message: Optional[str]


class CoreEngine:
    """
    Production-ready core engine with:
    - Dependency injection
    - Lifecycle management
    - Health monitoring
    - Graceful shutdown
    - Structured logging
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self, config_path: Optional[str] = None):
        if self._initialized:
            return
        
        self._initialized = True
        self.status = EngineStatus.INITIALIZING
        self.modules: Dict[str, ModuleInfo] = {}
        self._shutdown_handlers: List[Callable] = []
        self._start_time = datetime.now()
        self._metrics: Dict[str, Any] = defaultdict(int)
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Setup logging
        self._setup_logging()
        
        # Setup signal handlers
        self._setup_signal_handlers()
        
        logger.info("Core Engine initialized")
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file"""
        if not config_path:
            config_path = os.environ.get("MAHA_CONFIG_PATH", "config/engine.yaml")
        
        config_path = Path(config_path)
        
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return self._get_default_config()
        
        try:
            import yaml
            with open(config_path) as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "engine": {
                "name": "maha-sales-engine",
                "version": "1.0.0",
                "environment": "production"
            },
            "database": {
                "path": "data/maha.db",
                "pool_size": 10,
                "timeout": 30
            },
            "logging": {
                "level": "INFO",
                "format": "json",
                "output": "console",
                "file_path": "logs/engine.log",
                "max_size": "100MB",
                "backup_count": 10
            },
            "security": {
                "require_auth": True,
                "rate_limit": 100,
                "rate_window": 60,
                "secret_key": os.environ.get("MAHA_SECRET_KEY", "change-me-in-production")
            },
            "api": {
                "host": "0.0.0.0",
                "port": 8000,
                "workers": 4,
                "timeout": 30
            }
        }
    
    def _setup_logging(self):
        """Setup structured logging"""
        log_config = self.config.get("logging", {})
        log_level = getattr(logging, log_config.get("level", "INFO"))
        log_format = log_config.get("format", "json")
        
        # Create logs directory
        log_path = Path(log_config.get("file_path", "logs/engine.log"))
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        if log_format == "json":
            formatter = logging.Formatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", "message": "%(message)s"}'
            )
        else:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # File handler with rotation
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=int(log_config.get("max_size", "100MB").replace("MB", "000000")),
            backupCount=log_config.get("backup_count", 10)
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def handle_signal(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            self.stop()
        
        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)
    
    def register_module(self, name: str, instance: Any):
        """Register module with engine"""
        self.modules[name] = ModuleInfo(
            name=name,
            instance=instance,
            status="registered",
            initialized_at=datetime.now().isoformat(),
            error_message=None
        )
        logger.info(f"Module registered: {name}")
    
    def get_module(self, name: str) -> Optional[Any]:
        """Get module instance"""
        module_info = self.modules.get(name)
        return module_info.instance if module_info else None
    
    def start(self):
        """Start engine"""
        self.status = EngineStatus.RUNNING
        self._start_time = datetime.now()
        logger.info("Core Engine started")
    
    def stop(self):
        """Stop engine gracefully"""
        self.status = EngineStatus.STOPPING
        logger.info("Stopping Core Engine...")
        
        # Run shutdown handlers
        for handler in self._shutdown_handlers:
            try:
                handler()
            except Exception as e:
                logger.error(f"Shutdown handler failed: {e}")
        
        self.status = EngineStatus.STOPPED
        logger.info("Core Engine stopped")
    
    def get_health(self) -> Dict[str, Any]:
        """Get engine health"""
        uptime = (datetime.now() - self._start_time).total_seconds()
        
        return {
            "status": self.status.value,
            "uptime_seconds": uptime,
            "modules": {
                name: {
                    "status": info.status,
                    "initialized_at": info.initialized_at,
                    "error": info.error_message
                }
                for name, info in self.modules.items()
            },
            "metrics": dict(self._metrics)
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get engine status"""
        return {
            "engine": self.config.get("engine", {}),
            "status": self.status.value,
            "modules": list(self.modules.keys()),
            "health": self.get_health()
        }


# Global engine instance
engine = CoreEngine()


def get_engine() -> CoreEngine:
    """Get global engine instance"""
    return engine


def main():
    """Test core engine"""
    engine = CoreEngine()
    engine.start()
    
    print(f"Engine status: {engine.get_status()}")
    
    engine.stop()


if __name__ == "__main__":
    main()
