#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Shared Utilities
Common utilities for the entire platform.
"""

import os
import sys
import json
import time
import uuid
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from functools import wraps
from dataclasses import dataclass, field
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.shared")


class ErrorCode(Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"


@dataclass
class AppError(Exception):
    """Application error"""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details
            }
        }


class IDGenerator:
    """Generate unique IDs"""
    
    @staticmethod
    def generate_id(prefix: str = "") -> str:
        """Generate unique ID"""
        timestamp = int(time.time() * 1000)
        random_part = uuid.uuid4().hex[:8]
        return f"{prefix}{timestamp}{random_part}"
    
    @staticmethod
    def generate_uuid() -> str:
        """Generate UUID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_short_id() -> str:
        """Generate short ID"""
        return uuid.uuid4().hex[:12]


class TimeUtils:
    """Time utilities"""
    
    @staticmethod
    def now_iso() -> str:
        """Get current time in ISO format"""
        return datetime.now().isoformat()
    
    @staticmethod
    def now_timestamp() -> int:
        """Get current timestamp"""
        return int(time.time())
    
    @staticmethod
    def parse_iso(iso_string: str) -> datetime:
        """Parse ISO datetime string"""
        return datetime.fromisoformat(iso_string)
    
    @staticmethod
    def is_expired(expires_at: str) -> bool:
        """Check if timestamp has expired"""
        try:
            expiry = datetime.fromisoformat(expires_at)
            return datetime.now() > expiry
        except:
            return True


class HashUtils:
    """Hash utilities"""
    
    @staticmethod
    def sha256(data: str) -> str:
        """Calculate SHA256 hash"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def md5(data: str) -> str:
        """Calculate MD5 hash"""
        return hashlib.md5(data.encode()).hexdigest()
    
    @staticmethod
    def generate_checksum(file_path: Path) -> str:
        """Generate file checksum"""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()


class JSONUtils:
    """JSON utilities"""
    
    @staticmethod
    def safe_json_loads(data: str, default: Any = None) -> Any:
        """Safe JSON parsing"""
        try:
            return json.loads(data)
        except:
            return default
    
    @staticmethod
    def safe_json_dumps(data: Any, default: str = "{}") -> str:
        """Safe JSON serialization"""
        try:
            return json.dumps(data, ensure_ascii=False)
        except:
            return default


class FileUtils:
    """File utilities"""
    
    @staticmethod
    def ensure_directory(path: Path):
        """Ensure directory exists"""
        path.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def read_file(path: Path, default: str = "") -> str:
        """Read file safely"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except:
            return default
    
    @staticmethod
    def write_file(path: Path, content: str):
        """Write file safely"""
        FileUtils.ensure_directory(path.parent)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)


def retry(max_attempts: int = 3, backoff_factor: float = 2.0):
    """Retry decorator"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(backoff_factor ** attempt)
            raise last_exception
        return wrapper
    return decorator


def measure_time(func):
    """Measure execution time decorator"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        logger.debug(f"{func.__name__} took {elapsed:.3f}s")
        return result
    return wrapper


def main():
    """Test utilities"""
    print("Shared utilities loaded")
    
    # Test ID generation
    id1 = IDGenerator.generate_id("test-")
    assert id1.startswith("test-")
    
    # Test time utils
    now = TimeUtils.now_iso()
    assert isinstance(now, str)
    
    # Test hash utils
    hash_value = HashUtils.sha256("test")
    assert len(hash_value) == 64
    
    print("All utility tests passed")


if __name__ == "__main__":
    main()
