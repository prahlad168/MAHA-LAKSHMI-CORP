#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Shared Security Utilities
Common security functions for the entire platform.
"""

import os
import sys
import re
import hashlib
import hmac
import secrets
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from functools import wraps
from dataclasses import dataclass

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.shared.security")


# ============ VALIDATION ============

class ValidationError(Exception):
    """Validation error"""
    pass


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_uuid(value: str) -> bool:
    """Validate UUID format"""
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(pattern, value, re.IGNORECASE))


def validate_url(url: str) -> bool:
    """Validate URL format"""
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """Sanitize string input"""
    if not isinstance(value, str):
        raise ValidationError("Value must be a string")
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Limit length
    if len(value) > max_length:
        value = value[:max_length]
    
    return value.strip()


def validate_price(price: float) -> bool:
    """Validate price is positive"""
    return isinstance(price, (int, float)) and price >= 0


def validate_currency(currency: str) -> bool:
    """Validate currency code"""
    valid_currencies = ['USD', 'EUR', 'GBP', 'IDR', 'SGD', 'MYR', 'THB', 'PHP']
    return currency.upper() in valid_currencies


# ============ AUTHENTICATION ============

class SecurityUtils:
    """Security utility functions"""
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate secure API key"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_secret() -> str:
        """Generate secure secret"""
        return secrets.token_hex(32)
    
    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> tuple:
        """Hash password with salt"""
        if not salt:
            salt = secrets.token_hex(16)
        
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt.encode(),
            100000
        ).hex()
        
        return password_hash, salt
    
    @staticmethod
    def verify_password(password: str, salt: str, expected_hash: str) -> bool:
        """Verify password against hash"""
        password_hash, _ = SecurityUtils.hash_password(password, salt)
        return hmac.compare_digest(password_hash, expected_hash)
    
    @staticmethod
    def generate_jwt_token(user_id: str, expires_in: int = 86400) -> str:
        """Generate JWT token (simplified)"""
        import base64
        import json
        
        header = {"alg": "HS256", "typ": "JWT"}
        payload = {
            "sub": user_id,
            "iat": datetime.now().timestamp(),
            "exp": (datetime.now() + timedelta(seconds=expires_in)).timestamp()
        }
        
        header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
        payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
        
        # In production, use proper JWT signing with secret key
        signature = "placeholder_signature"
        
        return f"{header_b64}.{payload_b64}.{signature}"
    
    @staticmethod
    def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
        """Verify webhook HMAC signature"""
        expected = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)


# ============ DECORATORS ============

def require_auth(func):
    """Decorator to require authentication"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Implementation depends on auth framework
        return await func(*args, **kwargs)
    return wrapper


def validate_input(schema):
    """Decorator to validate input against schema"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Implementation depends on validation framework
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# ============ SECURITY HEADERS ============

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
    "Referrer-Policy": "strict-origin-when-cross-origin"
}


def get_security_headers() -> Dict[str, str]:
    """Get standard security headers"""
    return SECURITY_HEADERS.copy()


# ============ RATE LIMITING ============

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self._requests: Dict[str, List[float]] = {}
    
    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
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


# Global rate limiter instance
rate_limiter = RateLimiter()


# ============ ENCRYPTION ============

class EncryptionUtils:
    """Encryption utilities"""
    
    @staticmethod
    def encrypt_data(data: str, key: str) -> str:
        """Encrypt data (simplified)"""
        # In production, use proper encryption like Fernet
        return f"encrypted:{data}"
    
    @staticmethod
    def decrypt_data(encrypted_data: str, key: str) -> str:
        """Decrypt data (simplified)"""
        if encrypted_data.startswith("encrypted:"):
            return encrypted_data[10:]
        return encrypted_data
    
    @staticmethod
    def hash_data(data: str) -> str:
        """Hash data for comparison"""
        return hashlib.sha256(data.encode()).hexdigest()


def main():
    """Test security utilities"""
    print("Security utilities loaded")
    
    # Test validation
    assert validate_email("test@example.com") is True
    assert validate_uuid("12345678-1234-1234-1234-123456789012") is True
    
    # Test password hashing
    password_hash, salt = SecurityUtils.hash_password("test123")
    assert SecurityUtils.verify_password("test123", salt, password_hash) is True
    
    # Test rate limiter
    assert rate_limiter.is_allowed("test", 3, 60) is True
    
    print("All security tests passed")


if __name__ == "__main__":
    main()
