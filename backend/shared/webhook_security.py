"""
MAHA LAKSHMI CORP - Webhook Security
Gumroad webhook signature verification and security utilities.
"""

import hmac
import hashlib
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class WebhookSecurity:
    """Webhook security utilities"""
    
    @staticmethod
    def verify_gumroad_signature(payload: str, signature: str, secret: str) -> bool:
        """Verify Gumroad webhook signature"""
        if not secret or not signature:
            return False
        
        # Gumroad uses HMAC-SHA256
        expected = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected, signature)
    
    @staticmethod
    def extract_event_type(payload: Dict[str, Any]) -> Optional[str]:
        """Extract event type from Gumroad webhook payload"""
        # Gumroad webhook payload structure
        if "event" in payload:
            return payload["event"]
        elif "type" in payload:
            return payload["type"]
        elif "purchase" in payload:
            return "purchase"
        elif "refund" in payload:
            return "refund"
        elif "chargeback" in payload:
            return "chargeback"
        return None
    
    @staticmethod
    def is_replay_attack(event_id: str, timestamp: str, window_seconds: int = 300) -> bool:
        """Check for replay attacks"""
        try:
            event_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            now = datetime.now(event_time.tzinfo)
            age = (now - event_time).total_seconds()
            return age > window_seconds
        except Exception:
            return True
    
    @staticmethod
    def sanitize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize webhook payload for logging"""
        sensitive_keys = ["email", "name", "address", "phone", "license_key", "ip_address"]
        sanitized = payload.copy()
        
        for key in sensitive_keys:
            if key in sanitized:
                sanitized[key] = "***REDACTED***"
        
        return sanitized
