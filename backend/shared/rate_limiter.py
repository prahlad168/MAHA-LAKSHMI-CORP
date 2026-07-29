"""
MAHA LAKSHMI CORP - Rate Limiter
Production-grade rate limiting with Redis support.
"""

import time
import threading
from typing import Dict, Tuple, Optional
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from fastapi import Request, HTTPException

logger = __import__('logging').getLogger(__name__)


@dataclass
class RateLimitRule:
    """Rate limit rule"""
    max_requests: int
    window_seconds: int
    scope: str = "ip"  # ip, user, global


@dataclass
class ClientBucket:
    """Client rate limit bucket"""
    requests: int = 0
    window_start: float = field(default_factory=time.time)
    blocked_until: float = 0
    
    def is_blocked(self) -> bool:
        return time.time() < self.blocked_until
    
    def reset_if_expired(self, window_seconds: int):
        """Reset bucket if window expired"""
        if time.time() - self.window_start > window_seconds:
            self.requests = 0
            self.window_start = time.time()
            self.blocked_until = 0


class InMemoryRateLimiter:
    """In-memory rate limiter for single instance"""
    
    def __init__(self):
        self.buckets: Dict[str, ClientBucket] = {}
        self._lock = threading.Lock()
    
    def is_allowed(self, key: str, rule: RateLimitRule) -> Tuple[bool, Dict[str, int]]:
        """Check if request is allowed"""
        with self._lock:
            bucket = self.buckets.get(key)
            if not bucket:
                bucket = ClientBucket()
                self.buckets[key] = bucket
            
            # Check if blocked
            if bucket.is_blocked():
                return False, {
                    "limit": rule.max_requests,
                    "remaining": 0,
                    "reset": int(bucket.blocked_until),
                    "retry_after": int(bucket.blocked_until - time.time())
                }
            
            # Reset if window expired
            bucket.reset_if_expired(rule.window_seconds)
            
            # Check limit
            if bucket.requests >= rule.max_requests:
                # Block client
                bucket.blocked_until = time.time() + rule.window_seconds
                return False, {
                    "limit": rule.max_requests,
                    "remaining": 0,
                    "reset": int(bucket.blocked_until),
                    "retry_after": rule.window_seconds
                }
            
            # Allow request
            bucket.requests += 1
            return True, {
                "limit": rule.max_requests,
                "remaining": rule.max_requests - bucket.requests,
                "reset": int(bucket.window_start + rule.window_seconds)
            }
    
    def reset(self, key: Optional[str] = None):
        """Reset rate limits"""
        with self._lock:
            if key:
                self.buckets.pop(key, None)
            else:
                self.buckets.clear()


class RedisRateLimiter:
    """Redis-backed rate limiter for distributed systems"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def is_allowed(self, key: str, rule: RateLimitRule) -> Tuple[bool, Dict[str, int]]:
        """Check if request is allowed using Redis sliding window"""
        pipe = self.redis.pipeline()
        now = time.time()
        window_start = now - rule.window_seconds
        
        # Remove old entries
        pipe.zremrangebyscore(key, 0, window_start)
        # Count current requests
        pipe.zcard(key)
        # Add current request
        pipe.zadd(key, {str(now): now})
        # Set expiration
        pipe.expire(key, rule.window_seconds + 1)
        
        results = pipe.execute()
        current_count = results[1]
        
        if current_count >= rule.max_requests:
            # Get oldest request time
            oldest = self.redis.zrange(key, 0, 0, withscores=True)
            reset_time = int(oldest[0][1] + rule.window_seconds) if oldest else int(now + rule.window_seconds)
            return False, {
                "limit": rule.max_requests,
                "remaining": 0,
                "reset": reset_time,
                "retry_after": reset_time - int(now)
            }
        
        return True, {
            "limit": rule.max_requests,
            "remaining": rule.max_requests - current_count - 1,
            "reset": int(now + rule.window_seconds)
        }


# Global rate limiter instance
rate_limiter = InMemoryRateLimiter()


def rate_limit(max_requests: int = 100, window_seconds: int = 60, scope: str = "ip"):
    """Rate limiting decorator"""
    rule = RateLimitRule(max_requests=max_requests, window_seconds=window_seconds, scope=scope)
    
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            # Get client identifier
            if scope == "ip":
                key = f"ratelimit:{request.client.host}:{func.__name__}"
            elif scope == "user":
                auth_header = request.headers.get("authorization", "")
                if auth_header.startswith("Bearer "):
                    key = f"ratelimit:user:{auth_header[7:]}:{func.__name__}"
                else:
                    key = f"ratelimit:anonymous:{request.client.host}:{func.__name__}"
            else:
                key = f"ratelimit:global:{func.__name__}"
            
            allowed, info = rate_limiter.is_allowed(key, rule)
            
            # Add rate limit headers
            response = kwargs.get("response")
            if response:
                response.headers["X-RateLimit-Limit"] = str(info["limit"])
                response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
                response.headers["X-RateLimit-Reset"] = str(info["reset"])
            
            if not allowed:
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded",
                    headers={
                        "Retry-After": str(info.get("retry_after", window_seconds))
                    }
                )
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
