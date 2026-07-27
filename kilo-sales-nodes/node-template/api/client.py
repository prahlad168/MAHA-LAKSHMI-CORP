#!/usr/bin/env python3
"""
KILO SALES NODE - Encrypted HTTPS API Client
Handles all communication with the central dashboard.
"""

import os
import sys
import json
import time
import hmac
import hashlib
import requests
import ssl
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path

# Configuration
DASHBOARD_URL = os.getenv("KILO_DASHBOARD_URL", "https://mahalaksmi.web.id")
API_VERSION = "v1"
CERT_PATH = os.getenv("KILO_CERT_PATH", "/etc/ssl/node.crt")
KEY_PATH = os.getenv("KILO_KEY_PATH", "/etc/ssl/node.key")
CA_PATH = os.getenv("KILO_CA_PATH", "/etc/ssl/ca.crt")
NODE_ID = os.getenv("KILO_NODE_ID", "node-1")
NODE_SECRET = os.getenv("KILO_NODE_SECRET", "")


class KiloAPIClient:
    """Encrypted HTTPS API client for node-dashboard communication"""
    
    def __init__(self):
        self.base_url = f"{DASHBOARD_URL}/api/{API_VERSION}"
        self.node_id = NODE_ID
        self.node_secret = NODE_SECRET
        self.jwt_token = None
        self.token_expires = None
        self.ssl_context = self._create_ssl_context()
    
    def _create_ssl_context(self) -> Optional[ssl.SSLContext]:
        """Create mTLS SSL context"""
        cert = Path(CERT_PATH)
        key = Path(KEY_PATH)
        ca = Path(CA_PATH)
        
        if not all([cert.exists(), key.exists(), ca.exists()]):
            return None
        
        context = ssl.create_default_context(
            purpose=ssl.Purpose.SERVER_AUTH,
            cafile=str(ca)
        )
        context.load_cert_chain(certfile=str(cert), keyfile=str(key))
        context.check_hostname = True
        return context
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with JWT token"""
        headers = {
            "Content-Type": "application/json",
            "X-Node-ID": self.node_id,
            "X-Timestamp": datetime.now().isoformat()
        }
        
        if self.jwt_token and (not self.token_expires or datetime.now() < self.token_expires):
            headers["Authorization"] = f"Bearer {self.jwt_token}"
        
        return headers
    
    def _sign_request(self, data: str) -> str:
        """Sign request data with node secret"""
        return hmac.new(
            self.node_secret.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """Make authenticated HTTPS request"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        
        # Sign request if we have a secret
        if self.node_secret and data:
            signature = self._sign_request(json.dumps(data, sort_keys=True))
            headers["X-Signature"] = signature
        
        try:
            kwargs = {
                "headers": headers,
                "timeout": 30,
                "verify": str(CA_PATH) if Path(CA_PATH).exists() else True
            }
            
            if self.ssl_context:
                kwargs["verify"] = str(CA_PATH) if Path(CA_PATH).exists() else True
            
            if data:
                kwargs["json"] = data
            
            response = requests.request(method, url, **kwargs)
            
            if response.status_code == 401:
                # Token expired, try to refresh
                if self._refresh_token():
                    return self._request(method, endpoint, data)
                return None
            
            response.raise_for_status()
            return response.json() if response.text else {}
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None
    
    def _refresh_token(self) -> bool:
        """Refresh JWT token"""
        try:
            payload = {
                "node_id": self.node_id,
                "secret": self._sign_request(self.node_id)
            }
            
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=payload,
                timeout=10,
                verify=str(CA_PATH) if Path(CA_PATH).exists() else True,
                cert=(CERT_PATH, KEY_PATH) if Path(CERT_PATH).exists() else None
            )
            
            if response.status_code == 200:
                data = response.json()
                self.jwt_token = data.get("token")
                expires_in = data.get("expires_in", 86400)
                self.token_expires = datetime.now() + timedelta(seconds=expires_in)
                return True
            
            return False
            
        except Exception as e:
            print(f"Token refresh failed: {e}")
            return False
    
    def login(self) -> bool:
        """Authenticate with dashboard"""
        try:
            payload = {
                "node_id": self.node_id,
                "secret": self._sign_request(self.node_id)
            }
            
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=payload,
                timeout=10,
                verify=str(CA_PATH) if Path(CA_PATH).exists() else True,
                cert=(CERT_PATH, KEY_PATH) if Path(CERT_PATH).exists() else None
            )
            
            if response.status_code == 200:
                data = response.json()
                self.jwt_token = data.get("token")
                expires_in = data.get("expires_in", 86400)
                self.token_expires = datetime.now() + timedelta(seconds=expires_in)
                print(f"✅ Node {self.node_id} authenticated")
                return True
            
            print(f"❌ Authentication failed: {response.status_code}")
            return False
            
        except Exception as e:
            print(f"Login error: {e}")
            return False
    
    def register(self, node_info: Dict[str, Any]) -> Optional[Dict]:
        """Register node with dashboard"""
        return self._request("POST", "/nodes/register", data=node_info)
    
    def heartbeat(self, metrics: Dict[str, Any]) -> bool:
        """Send heartbeat to dashboard"""
        payload = {
            "node_id": self.node_id,
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics
        }
        result = self._request("POST", "/nodes/heartbeat", data=payload)
        return result is not None
    
    def send_report(self, report: Dict[str, Any]) -> Optional[Dict]:
        """Send daily report to dashboard"""
        payload = {
            "node_id": self.node_id,
            **report
        }
        return self._request("POST", "/nodes/report", data=payload)
    
    def get_commands(self, since: Optional[str] = None) -> Dict[str, Any]:
        """Get commands from dashboard"""
        params = {}
        if since:
            params["since"] = since
        
        url = f"/nodes/commands"
        if params:
            url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
        
        result = self._request("GET", url)
        return result or {"commands": []}
    
    def get_products(self, market: Optional[str] = None) -> Dict[str, Any]:
        """Get product listings from dashboard"""
        params = {}
        if market:
            params["market"] = market
        
        url = "/products"
        if params:
            url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
        
        result = self._request("GET", url)
        return result or {"products": []}
    
    def update_status(self, status: Dict[str, Any]) -> bool:
        """Update node status"""
        result = self._request("POST", "/nodes/status", data=status)
        return result is not None


def main():
    """Test API client"""
    client = KiloAPIClient()
    
    # Test authentication
    if client.login():
        print("✅ Authentication successful")
        
        # Test heartbeat
        if client.heartbeat({"cpu_usage": 0.0, "memory_usage": 8.0}):
            print("✅ Heartbeat sent")
    else:
        print("❌ Authentication failed")


if __name__ == "__main__":
    main()
