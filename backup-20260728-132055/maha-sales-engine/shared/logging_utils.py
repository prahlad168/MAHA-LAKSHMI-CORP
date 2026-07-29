#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Structured Logging System
Production-ready logging with JSON formatting, rotation, and monitoring hooks.
"""

import os
import sys
import json
import time
import logging
import traceback
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
from functools import wraps
from dataclasses import dataclass, field, asdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.logging")


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LogEntry:
    timestamp: str
    level: str
    logger: str
    message: str
    module: str
    function: str
    line: int
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    traceback: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


class JSONFormatter(logging.Formatter):
    """JSON log formatter"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            level=record.levelname,
            logger=record.name,
            message=record.getMessage(),
            module=record.module,
            function=record.funcName,
            line=record.lineno,
            extra=getattr(record, 'extra', {})
        )
        
        # Add exception info
        if record.exc_info and record.exc_info[0]:
            log_entry.traceback = ''.join(traceback.format_exception(*record.exc_info))
        
        return log_entry.to_json()


class StructuredLogger:
    """Production-ready structured logger"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(f"maha-sales-engine.{name}")
        self._request_id: Optional[str] = None
    
    def set_request_id(self, request_id: str):
        """Set request ID for correlation"""
        self._request_id = request_id
    
    def _log(self, level: str, message: str, **kwargs):
        """Log with structured data"""
        extra = {
            "request_id": self._request_id,
            **kwargs
        }
        
        log_method = getattr(self.logger, level.lower())
        log_method(message, extra={"extra": extra})
    
    def debug(self, message: str, **kwargs):
        self._log("DEBUG", message, **kwargs)
    
    def info(self, message: str, **kwargs):
        self._log("INFO", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log("WARNING", message, **kwargs)
    
    def error(self, message: str, error: Optional[Exception] = None, **kwargs):
        if error:
            kwargs["error_type"] = type(error).__name__
            kwargs["error_message"] = str(error)
            kwargs["traceback"] = traceback.format_exc()
        self._log("ERROR", message, **kwargs)
    
    def critical(self, message: str, error: Optional[Exception] = None, **kwargs):
        if error:
            kwargs["error_type"] = type(error).__name__
            kwargs["error_message"] = str(error)
            kwargs["traceback"] = traceback.format_exc()
        self._log("CRITICAL", message, **kwargs)


class LoggingManager:
    """Central logging configuration"""
    
    def __init__(self):
        self._loggers: Dict[str, StructuredLogger] = {}
        self._handlers: List[logging.Handler] = []
    
    def setup(self, config: Dict[str, Any]):
        """Setup logging from configuration"""
        log_level = getattr(logging, config.get("level", "INFO"))
        log_format = config.get("format", "json")
        
        # Create logs directory
        log_path = Path(config.get("file_path", "logs/engine.log"))
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Console handler
        console_handler = self._create_console_handler(log_level, log_format)
        root_logger.addHandler(console_handler)
        
        # File handler with rotation
        file_handler = self._create_file_handler(log_path, log_level, config)
        root_logger.addHandler(file_handler)
        
        # Error file handler
        error_handler = self._create_error_handler(log_path, log_level)
        root_logger.addHandler(error_handler)
        
        logger.info("Logging system initialized")
    
    def _create_console_handler(self, level: int, log_format: str) -> logging.Handler:
        """Create console handler"""
        handler = logging.StreamHandler()
        handler.setLevel(level)
        
        if log_format == "json":
            handler.setFormatter(JSONFormatter())
        else:
            handler.setFormatter(logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            ))
        
        return handler
    
    def _create_file_handler(self, log_path: Path, level: int, config: Dict) -> logging.Handler:
        """Create rotating file handler"""
        from logging.handlers import RotatingFileHandler
        
        max_size = self._parse_size(config.get("max_size", "100MB"))
        backup_count = config.get("backup_count", 10)
        
        handler = RotatingFileHandler(
            log_path,
            maxBytes=max_size,
            backupCount=backup_count
        )
        handler.setLevel(level)
        handler.setFormatter(JSONFormatter())
        return handler
    
    def _create_error_handler(self, log_path: Path, level: int) -> logging.Handler:
        """Create error-only file handler"""
        from logging.handlers import RotatingFileHandler
        
        error_path = log_path.parent / f"{log_path.stem}_errors{log_path.suffix}"
        
        handler = RotatingFileHandler(
            error_path,
            maxBytes=10*1024*1024,
            backupCount=5
        )
        handler.setLevel(logging.ERROR)
        handler.setFormatter(JSONFormatter())
        return handler
    
    def _parse_size(self, size_str: str) -> int:
        """Parse size string like '100MB' to bytes"""
        size_str = size_str.upper().strip()
        multipliers = {
            'GB': 1024*1024*1024,
            'MB': 1024*1024,
            'KB': 1024,
            'B': 1
        }
        
        for suffix, multiplier in multipliers.items():
            if size_str.endswith(suffix):
                number_part = size_str[:-len(suffix)].strip()
                return int(float(number_part) * multiplier)
        
        return int(size_str)
    
    def get_logger(self, name: str) -> StructuredLogger:
        """Get structured logger"""
        if name not in self._loggers:
            self._loggers[name] = StructuredLogger(name)
        return self._loggers[name]


# Global logging manager
logging_manager = LoggingManager()


def get_logger(name: str) -> StructuredLogger:
    """Get structured logger"""
    return logging_manager.get_logger(name)


def log_execution_time(func):
    """Decorator to log execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            logger.info(f"{func.__name__} completed in {elapsed:.3f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start
            logger.error(f"{func.__name__} failed after {elapsed:.3f}s: {e}")
            raise
    return wrapper


def log_request(func):
    """Decorator to log API requests"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = kwargs.get("request")
        request_id = getattr(request, "state", {}).get("request_id", "unknown")
        
        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={"request_id": request_id}
        )
        
        start = time.time()
        try:
            result = await func(*args, **kwargs)
            elapsed = time.time() - start
            logger.info(
                f"Response: {result.status_code} ({elapsed:.3f}s)",
                extra={"request_id": request_id}
            )
            return result
        except Exception as e:
            elapsed = time.time() - start
            logger.error(
                f"Request failed: {e} ({elapsed:.3f}s)",
                extra={"request_id": request_id}
            )
            raise
    return wrapper


def main():
    """Test logging system"""
    print("Logging system loaded")
    
    test_logger = get_logger("test")
    test_logger.info("Test log entry", extra={"key": "value"})


if __name__ == "__main__":
    main()
