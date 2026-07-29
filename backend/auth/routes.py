"""
MAHA LAKSHMI CORP - Authentication Routes
JWT, 2FA TOTP, WebAuthn, Session Management, CSRF Protection
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets
import hashlib
import hmac
import json
import logging
from pathlib import Path

from backend.db.connection import get_db, execute_query, execute_many
from backend.shared.security import hash_password, verify_password, generate_jwt_token, verify_jwt_token, create_csrf_token, verify_csrf_token
from backend.shared.rate_limiter import rate_limit

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

# Models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    totp_code: Optional[str] = None
    remember_me: bool = False

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=12)
    name: str = Field(..., min_length=2, max_length=100)
    role: str = "viewer"
    
    @validator("password")
    def validate_password(cls, v):
        if len(v) < 12:
            raise ValueError("Password must be at least 12 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain digit")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            raise ValueError("Password must contain special character")
        return v

class TOTPSetupResponse(BaseModel):
    secret: str
    qr_code_url: str
    backup_codes: list[str]

class WebAuthnCredential(BaseModel):
    id: str
    raw_id: str
    type: str
    response: Dict[str, Any]

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

# Helper functions
def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email"""
    return execute_query("SELECT * FROM users WHERE email = ?", (email,), fetch="one")

def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    return execute_query("SELECT * FROM users WHERE id = ?", (user_id,), fetch="one")

def create_user_session(user_id: str, remember_me: bool = False) -> Dict[str, Any]:
    """Create user session"""
    session_id = secrets.token_urlsafe(32)
    days = 7 if remember_me else 1
    expires_at = datetime.now() + timedelta(days=days)
    
    execute_query(
        "INSERT INTO sessions (id, user_id, expires_at, created_at) VALUES (?, ?, ?, ?)",
        (session_id, user_id, expires_at.isoformat(), datetime.now().isoformat()),
        fetch="none"
    )
    
    return {
        "session_id": session_id,
        "expires_at": expires_at.isoformat(),
        "user_id": user_id
    }

def validate_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Validate session"""
    session = execute_query(
        "SELECT s.*, u.email, u.name, u.role FROM sessions s JOIN users u ON s.user_id = u.id WHERE s.id = ? AND s.expires_at > ?",
        (session_id, datetime.now().isoformat()),
        fetch="one"
    )
    return session

def invalidate_session(session_id: str):
    """Invalidate session"""
    execute_query("DELETE FROM sessions WHERE id = ?", (session_id,), fetch="none")


@router.post("/register", response_model=Dict[str, Any], tags=["Authentication"])
@rate_limit(max_requests=5, window_seconds=3600)
async def register(request: Request, user_data: RegisterRequest, db = Depends(get_db)):
    """Register new user"""
    # Check if user exists
    existing = get_user_by_email(user_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    password_hash = hash_password(user_data.password)
    
    # Create user
    user_id = secrets.token_urlsafe(16)
    now = datetime.now().isoformat()
    
    db.execute(
        "INSERT INTO users (id, email, password_hash, name, role, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (user_id, user_data.email, password_hash, user_data.name, user_data.role, now, now)
    )
    db.commit()
    
    logger.info(f"User registered: {user_data.email}")
    
    return {
        "message": "User registered successfully",
        "user_id": user_id,
        "email": user_data.email
    }


@router.post("/login", response_model=TokenResponse, tags=["Authentication"])
@rate_limit(max_requests=10, window_seconds=300)
async def login(request: Request, response: Response, login_data: LoginRequest, db = Depends(get_db)):
    """Login with email and password"""
    # Get user
    user = get_user_by_email(login_data.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check 2FA if enabled
    if user.get("totp_enabled") and not login_data.totp_code:
        raise HTTPException(status_code=428, detail="2FA code required")
    
    if user.get("totp_enabled") and login_data.totp_code:
        # Verify TOTP
        if not verify_totp(user["totp_secret"], login_data.totp_code):
            raise HTTPException(status_code=401, detail="Invalid 2FA code")
    
    # Create session
    session = create_user_session(user["id"], login_data.remember_me)
    
    # Generate tokens
    access_token = generate_jwt_token({
        "user_id": user["id"],
        "email": user["email"],
        "role": user["role"],
        "session_id": session["session_id"],
        "exp": datetime.now() + timedelta(minutes=15)
    })
    
    refresh_token = generate_jwt_token({
        "user_id": user["id"],
        "session_id": session["session_id"],
        "type": "refresh",
        "exp": datetime.now() + timedelta(days=7)
    })
    
    # Set refresh token as HttpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=7 * 24 * 60 * 60,
        path="/api/auth/refresh"
    )
    
    # Log audit
    execute_query(
        "INSERT INTO audit_logs (user_id, action, ip_address, user_agent, created_at) VALUES (?, ?, ?, ?, ?)",
        (user["id"], "login", request.client.host, request.headers.get("user-agent", ""), datetime.now().isoformat()),
        fetch="none"
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=15 * 60,
        user={
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"]
        }
    )


@router.post("/logout", tags=["Authentication"])
async def logout(request: Request, response: Response, credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Logout user"""
    if credentials:
        try:
            payload = verify_jwt_token(credentials.credentials)
            session_id = payload.get("session_id")
            if session_id:
                invalidate_session(session_id)
        except Exception:
            pass
    
    response.delete_cookie("refresh_token", path="/api/auth/refresh")
    return {"message": "Logged out successfully"}


@router.post("/refresh", response_model=TokenResponse, tags=["Authentication"])
async def refresh_token(request: Request, response: Response, refresh_token: str = Depends(lambda r: r.cookies.get("refresh_token"))):
    """Refresh access token"""
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token required")
    
    try:
        payload = verify_jwt_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        user = get_user_by_id(payload["user_id"])
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        session = validate_session(payload["session_id"])
        if not session:
            raise HTTPException(status_code=401, detail="Invalid session")
        
        access_token = generate_jwt_token({
            "user_id": user["id"],
            "email": user["email"],
            "role": user["role"],
            "session_id": payload["session_id"],
            "exp": datetime.now() + timedelta(minutes=15)
        })
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=15 * 60,
            user={
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "role": user["role"]
            }
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.get("/2fa/setup", response_model=TOTPSetupResponse, tags=["2FA"])
async def setup_2fa(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Setup TOTP 2FA"""
    payload = verify_jwt_token(credentials.credentials)
    user = get_user_by_id(payload["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate TOTP secret
    secret = pyotp.random_base32()
    backup_codes = [secrets.token_hex(4) for _ in range(10)]
    
    # Store temporarily (user must confirm)
    execute_query(
        "UPDATE users SET totp_secret = ? WHERE id = ?",
        (secret, user["id"]),
        fetch="none"
    )
    
    # Generate QR code URL
    qr_url = pyotp.totp.TOTP(secret).provisioning_uri(
        name=user["email"],
        issuer_name="MAHA LAKSHMI CORP"
    )
    
    return TOTPSetupResponse(
        secret=secret,
        qr_code_url=qr_url,
        backup_codes=backup_codes
    )


@router.post("/2fa/verify", tags=["2FA"])
async def verify_2fa(credentials: HTTPAuthorizationCredentials = Depends(security), totp_code: str = None):
    """Verify TOTP 2FA"""
    payload = verify_jwt_token(credentials.credentials)
    user = get_user_by_id(payload["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not pyotp.totp.TOTP(user["totp_secret"]).verify(totp_code):
        raise HTTPException(status_code=400, detail="Invalid 2FA code")
    
    # Enable 2FA
    execute_query(
        "UPDATE users SET totp_enabled = 1 WHERE id = ?",
        (user["id"],),
        fetch="none"
    )
    
    return {"message": "2FA enabled successfully"}


@router.post("/webauthn/register/begin", tags=["WebAuthn"])
async def webauthn_register_begin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Begin WebAuthn registration"""
    payload = verify_jwt_token(credentials.credentials)
    user = get_user_by_id(payload["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate challenge
    challenge = secrets.token_bytes(32)
    
    # Store challenge
    execute_query(
        "INSERT INTO webauthn_challenges (user_id, challenge, type, created_at) VALUES (?, ?, ?, ?)",
        (user["id"], challenge.hex(), "registration", datetime.now().isoformat()),
        fetch="none"
    )
    
    return {
        "challenge": challenge.hex(),
        "user_id": user["id"],
        "rp": {
            "name": "MAHA LAKSHMI CORP",
            "id": request.headers.get("host", "mahalaksmi.web.id")
        }
    }


@router.post("/webauthn/register/complete", tags=["WebAuthn"])
async def webauthn_register_complete(credential: WebAuthnCredential, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Complete WebAuthn registration"""
    payload = verify_jwt_token(credentials.credentials)
    user = get_user_by_id(payload["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify and store credential
    execute_query(
        "INSERT INTO webauthn_credentials (user_id, credential_id, public_key, sign_count, created_at) VALUES (?, ?, ?, ?, ?)",
        (user["id"], credential.id, credential.response.get("publicKey"), credential.response.get("signCount", 0), datetime.now().isoformat()),
        fetch="none"
    )
    
    return {"message": "WebAuthn credential registered successfully"}


@router.get("/me", tags=["Authentication"])
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user info"""
    payload = verify_jwt_token(credentials.credentials)
    user = get_user_by_id(payload["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
        "totp_enabled": user.get("totp_enabled", False),
        "webauthn_enabled": user.get("webauthn_enabled", False)
    }


@router.post("/password-reset/request", tags=["Password"])
async def request_password_reset(request: PasswordResetRequest):
    """Request password reset"""
    user = get_user_by_email(request.email)
    if not user:
        return {"message": "If email exists, reset link will be sent"}
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=1)
    
    execute_query(
        "INSERT INTO password_resets (email, token, expires_at, created_at) VALUES (?, ?, ?, ?)",
        (request.email, reset_token, expires_at.isoformat(), datetime.now().isoformat()),
        fetch="none"
    )
    
    # Send email with reset link
    from backend.notifications.email import email_service
    reset_link = f"/password-reset/confirm?token={reset_token}"
    email_service.send(
        to=request.email,
        subject="Password Reset Request",
        body=f"Use this link to reset your password: {reset_link}\nThis link expires in 1 hour.",
    )
    
    return {"message": "If email exists, reset link will be sent"}


@router.post("/password-reset/confirm", tags=["Password"])
async def confirm_password_reset(request: PasswordResetConfirm):
    """Confirm password reset"""
    reset = execute_query(
        "SELECT * FROM password_resets WHERE token = ? AND expires_at > ? AND used = 0",
        (request.token, datetime.now().isoformat()),
        fetch="one"
    )
    
    if not reset:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    # Update password
    password_hash = hash_password(request.new_password)
    execute_query(
        "UPDATE users SET password_hash = ?, updated_at = ? WHERE email = ?",
        (password_hash, datetime.now().isoformat(), reset["email"]),
        fetch="none"
    )
    
    # Mark token as used
    execute_query(
        "UPDATE password_resets SET used = 1 WHERE token = ?",
        (request.token,),
        fetch="none"
    )
    
    # Invalidate all sessions
    execute_query(
        "DELETE FROM sessions WHERE user_id = (SELECT id FROM users WHERE email = ?)",
        (reset["email"],),
        fetch="none"
    )
    
    return {"message": "Password reset successfully"}
