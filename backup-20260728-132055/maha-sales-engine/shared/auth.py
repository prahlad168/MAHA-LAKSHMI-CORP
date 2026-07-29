#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Shared Authentication Middleware
Production-ready authentication and authorization for all APIs.
"""

import os
import sys
import json
import time
import logging
import secrets
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from functools import wraps
from dataclasses import dataclass
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.security import SecurityUtils, validate_email, validate_uuid

logger = logging.getLogger("maha-sales-engine.shared.auth")


class UserRole(Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"
    SYSTEM = "system"


class Permission(Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


@dataclass
class User:
    user_id: str
    email: str
    role: str
    permissions: List[str]
    api_key: str
    is_active: bool
    created_at: str


@dataclass
class AuthContext:
    user: Optional[User]
    api_key: str
    permissions: List[str]
    is_authenticated: bool


class AuthenticationError(Exception):
    """Authentication error"""
    pass


class AuthorizationError(Exception):
    """Authorization error"""
    pass


class AuthManager:
    """Manage authentication and authorization"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self._api_keys: Dict[str, User] = {}
        self._rate_limiter = RateLimiter()
    
    def create_user(self, email: str, role: str, permissions: List[str]) -> Optional[str]:
        """Create new user"""
        try:
            if not validate_email(email):
                raise ValidationError("Invalid email")
            
            user_id = f"user-{int(time.time() * 1000)}-{secrets.token_hex(4)}"
            api_key = SecurityUtils.generate_api_key()
            
            user = User(
                user_id=user_id,
                email=email,
                role=role,
                permissions=permissions,
                api_key=api_key,
                is_active=True,
                created_at=datetime.now().isoformat()
            )
            
            self._save_user(user)
            self._api_keys[api_key] = user
            
            logger.info(f"User created: {user_id}")
            return api_key
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return None
    
    def authenticate(self, api_key: str) -> Optional[AuthContext]:
        """Authenticate request"""
        try:
            user = self._api_keys.get(api_key)
            if not user:
                user = self._load_user_by_api_key(api_key)
            else:
                # Check if user is still active in DB
                db_user = self._load_user_by_api_key(api_key)
                if db_user and not db_user.is_active:
                    return None
                if db_user:
                    user = db_user
                    self._api_keys[api_key] = user
            
            if not user or not user.is_active:
                return None
            
            return AuthContext(
                user=user,
                api_key=api_key,
                permissions=user.permissions,
                is_authenticated=True
            )
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return None
    
    def authorize(self, auth_context: AuthContext, required_permission: str) -> bool:
        """Check authorization"""
        if not auth_context.is_authenticated:
            return False
        
        if Permission.ADMIN.value in auth_context.permissions:
            return True
        
        return required_permission in auth_context.permissions
    
    def _save_user(self, user: User):
        """Save user to database"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users (user_id, email, role, permissions, api_key, is_active, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    user.user_id, user.email, user.role,
                    json.dumps(user.permissions), user.api_key,
                    user.is_active, user.created_at
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to save user: {e}")
            raise
    
    def _load_user_by_api_key(self, api_key: str) -> Optional[User]:
        """Load user by API key"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE api_key = ?", (api_key,))
                row = cursor.fetchone()
                
                if row:
                    permissions_raw = row["permissions"] if "permissions" in row.keys() else "[]"
                    return User(
                        user_id=row["user_id"],
                        email=row["email"],
                        role=row["role"],
                        permissions=json.loads(permissions_raw),
                        api_key=row["api_key"],
                        is_active=bool(row["is_active"]),
                        created_at=row["created_at"]
                    )
                return None
        except Exception as e:
            logger.error(f"Failed to load user: {e}")
            return None


class RateLimiter:
    """Rate limiter for API endpoints"""
    
    def __init__(self):
        self._requests: Dict[str, List[float]] = {}
    
    def is_allowed(self, key: str, max_requests: int = 100, window_seconds: int = 60) -> bool:
        """Check if request is allowed"""
        now = datetime.now().timestamp()
        
        if key not in self._requests:
            self._requests[key] = []
        
        # Remove old requests
        self._requests[key] = [
            req_time for req_time in self._requests[key]
            if now - req_time < window_seconds
        ]
        
        # Check limit
        if len(self._requests[key]) >= max_requests:
            return False
        
        # Add current request
        self._requests[key].append(now)
        return True


# ============ MIDDLEWARE ============

class AuthenticationMiddleware:
    """FastAPI authentication middleware"""
    
    def __init__(self, auth_manager: AuthManager):
        self.auth_manager = auth_manager
    
    async def __call__(self, request, call_next):
        # Skip auth for health checks and docs
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Extract API key
        api_key = request.headers.get("X-API-Key") or request.headers.get("Authorization", "").replace("Bearer ", "")
        
        if not api_key:
            return JSONResponse(
                status_code=401,
                content={"error": "Missing API key", "code": "AUTH_REQUIRED"}
            )
        
        # Authenticate
        auth_context = self.auth_manager.authenticate(api_key)
        if not auth_context:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid API key", "code": "AUTH_INVALID"}
            )
        
        # Add auth context to request
        request.state.auth = auth_context
        
        return await call_next(request)


class RateLimitMiddleware:
    """Rate limiting middleware"""
    
    def __init__(self, rate_limiter: RateLimiter):
        self.rate_limiter = rate_limiter
    
    async def __call__(self, request, call_next):
        # Skip rate limiting for health checks
        if request.url.path == "/health":
            return await call_next(request)
        
        # Get client identifier
        client_id = request.headers.get("X-Client-ID", request.client.host)
        
        # Check rate limit
        if not self.rate_limiter.is_allowed(client_id):
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded", "code": "RATE_LIMIT_EXCEEDED"}
            )
        
        return await call_next(request)


class SecurityHeadersMiddleware:
    """Add security headers to responses"""
    
    async def __call__(self, request, call_next):
        response = await call_next(request)
        
        headers = SecurityUtils.get_security_headers()
        for header, value in headers.items():
            response.headers[header] = value
        
        return response


def get_current_user(request) -> Optional[User]:
    """Get current user from request"""
    auth = getattr(request.state, "auth", None)
    return auth.user if auth else None


def require_permission(permission: str):
    """Decorator to require specific permission"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get("request")
            if not request:
                raise AuthenticationError("Request not found")
            
            auth = getattr(request.state, "auth", None)
            if not auth or not auth.is_authenticated:
                raise AuthenticationError("Not authenticated")
            
            if permission not in auth.permissions:
                raise AuthorizationError(f"Missing permission: {permission}")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def main():
    """Test authentication"""
    print("Authentication middleware loaded")


if __name__ == "__main__":
    main()
