#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Cache System
Redis-based caching with fallback to in-memory cache.
"""

import os
import sys
import json
import time
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import wraps

sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger("maha-sales-engine.cache")


class CacheError(Exception):
    """Cache error"""
    pass


@dataclass
class CacheEntry:
    key: str
    value: Any
    expires_at: Optional[str]
    created_at: str
    metadata: Dict[str, Any] = None
    
    def is_expired(self) -> bool:
        if not self.expires_at:
            return False
        return datetime.now() > datetime.fromisoformat(self.expires_at)


class InMemoryCache:
    """In-memory cache with TTL"""
    
    def __init__(self, max_size: int = 1000):
        self._cache: Dict[str, CacheEntry] = {}
        self._max_size = max_size
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            entry = self._cache[key]
            if not entry.is_expired():
                self._hits += 1
                return entry.value
            else:
                del self._cache[key]
        self._misses += 1
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        if len(self._cache) >= self._max_size:
            self._evict()
        
        expires_at = None
        if ttl:
            expires_at = (datetime.now() + timedelta(seconds=ttl)).isoformat()
        
        self._cache[key] = CacheEntry(
            key=key,
            value=value,
            expires_at=expires_at,
            created_at=datetime.now().isoformat()
        )
    
    def delete(self, key: str):
        self._cache.pop(key, None)
    
    def clear(self):
        self._cache.clear()
        self._hits = 0
        self._misses = 0
    
    def _evict(self):
        """Evict expired entries"""
        if self._max_size <= 0:
            self._cache.clear()
            return
        
        now = datetime.now()
        expired = [k for k, v in self._cache.items() if v.expires_at and now > datetime.fromisoformat(v.expires_at)]
        for key in expired:
            del self._cache[key]
        
        # If still full, remove oldest
        while len(self._cache) >= self._max_size and self._cache:
            oldest = min(self._cache.items(), key=lambda x: x[1].created_at)
            del self._cache[oldest[0]]
    
    def get_stats(self) -> Dict[str, Any]:
        total = self._hits + self._misses
        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(self._hits / total, 2) if total > 0 else 0
        }


class CacheManager:
    """Production cache manager with Redis and in-memory fallback"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self._redis_client = None
        self._memory_cache = InMemoryCache()
        
        if redis_url:
            try:
                import redis
                self._redis_client = redis.from_url(redis_url, decode_responses=True)
                self._redis_client.ping()
                logger.info("Redis cache connected")
            except Exception as e:
                logger.warning(f"Redis connection failed, using memory cache: {e}")
                self._redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if self._redis_client:
                value = self._redis_client.get(key)
                if value:
                    return json.loads(value)
            
            return self._memory_cache.get(key)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
        try:
            serialized = json.dumps(value)
            
            if self._redis_client:
                if ttl:
                    self._redis_client.setex(key, ttl, serialized)
                else:
                    self._redis_client.set(key, serialized)
            
            self._memory_cache.set(key, value, ttl)
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    def delete(self, key: str):
        """Delete key from cache"""
        try:
            if self._redis_client:
                self._redis_client.delete(key)
            self._memory_cache.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
    
    def clear(self):
        """Clear all cache"""
        try:
            if self._redis_client:
                self._redis_client.flushdb()
            self._memory_cache.clear()
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
    
    def get_or_set(self, key: str, factory, ttl: Optional[int] = None) -> Any:
        """Get from cache or set using factory"""
        value = self.get(key)
        if value is None:
            value = factory()
            self.set(key, value, ttl)
        return value
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = {
            "backend": "redis" if self._redis_client else "memory",
            "memory": self._memory_cache.get_stats()
        }
        
        if self._redis_client:
            try:
                info = self._redis_client.info()
                stats["redis"] = {
                    "used_memory": info.get("used_memory_human"),
                    "connected_clients": info.get("connected_clients"),
                    "keyspace_hits": info.get("keyspace_hits"),
                    "keyspace_misses": info.get("keyspace_misses")
                }
            except:
                pass
        
        return stats
    
    def close(self):
        """Close cache connections"""
        if self._redis_client:
            self._redis_client.close()


# Global cache instance
cache = CacheManager(os.environ.get("REDIS_URL"))


def get_cache() -> CacheManager:
    """Get global cache instance"""
    return cache


def cached(ttl: Optional[int] = None, key_prefix: str = ""):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key
            key_parts = [key_prefix or func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)
            
            # Try cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


def main():
    """Test cache system"""
    print("Cache system loaded")
    
    cache = CacheManager()
    cache.set("test-key", {"value": "test"}, ttl=60)
    result = cache.get("test-key")
    
    assert result == {"value": "test"}
    print("Cache tests passed")


if __name__ == "__main__":
    main()
