"""
MAHA LAKSHMI CORP - Security Utilities
JWT, Password Hashing, TOTP, WebAuthn, CSRF, Encryption
"""

import os
import secrets
import hashlib
import hmac
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import pyotp
import base64
from fastapi import HTTPException

# JWT Settings
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 15
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password Settings
PASSWORD_ITERATIONS = 100000
PASSWORD_KEY_LENGTH = 32
PASSWORD_SALT_LENGTH = 16


def hash_password(password: str) -> str:
    """Hash password using PBKDF2-HMAC-SHA256"""
    salt = secrets.token_bytes(PASSWORD_SALT_LENGTH)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        PASSWORD_ITERATIONS,
        dklen=PASSWORD_KEY_LENGTH
    )
    return f"pbkdf2_sha256${PASSWORD_ITERATIONS}${salt.hex()}${key.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    try:
        algorithm, iterations, salt_hex, key_hex = password_hash.split('$')
        iterations = int(iterations)
        salt = bytes.fromhex(salt_hex)
        expected_key = bytes.fromhex(key_hex)
        
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            iterations,
            dklen=len(expected_key)
        )
        
        return hmac.compare_digest(key, expected_key)
    except Exception:
        return False


def generate_jwt_token(payload: Dict[str, Any]) -> str:
    """Generate JWT token"""
    from jose import jwt
    
    expire = payload.get("exp", datetime.now() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
    payload["iat"] = datetime.now()
    payload["exp"] = expire
    
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_jwt_token(token: str) -> Dict[str, Any]:
    """Verify and decode JWT token"""
    from jose import jwt, JWTError
    
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def create_csrf_token() -> str:
    """Create CSRF token"""
    return secrets.token_urlsafe(32)


def verify_csrf_token(token: str, stored_token: str) -> bool:
    """Verify CSRF token"""
    return hmac.compare_digest(token, stored_token)


def generate_backup_codes(count: int = 10) -> list[str]:
    """Generate backup codes for 2FA"""
    return [secrets.token_hex(4).upper() for _ in range(count)]


def verify_totp(secret: str, code: str) -> bool:
    """Verify TOTP code"""
    if not secret or not code:
        return False
    
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)


class SecurityUtils:
    """Security utilities"""
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate API key"""
        return f"mlc_{secrets.token_urlsafe(32)}"
    
    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Hash API key for storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    @staticmethod
    def generate_webhook_signature(payload: str, secret: str) -> str:
        """Generate webhook signature"""
        return hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    @staticmethod
    def verify_webhook_signature(payload: str, signature: str, secret: str) -> bool:
        """Verify webhook signature"""
        expected = SecurityUtils.generate_webhook_signature(payload, secret)
        return hmac.compare_digest(expected, signature)
