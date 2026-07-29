#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Marketplace Credential Manager
Secure credential storage and management.
"""

import os
import json
import base64
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from cryptography.fernet import Fernet
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

logger = logging.getLogger("maha-sales-engine.marketplace.security.credentials")


class CredentialManager:
    """Secure credential management with encryption support"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        self.encryption_key = encryption_key or os.environ.get("MARKETPLACE_ENCRYPTION_KEY", "")
        self._credentials: Dict[str, Dict[str, Any]] = {}
        self._fernet = None
        
        if HAS_CRYPTO and self.encryption_key:
            try:
                key = base64.urlsafe_b64encode(self.encryption_key.encode()[:32].ljust(32, b'0'))
                self._fernet = Fernet(key)
            except Exception as e:
                logger.warning(f"Failed to initialize encryption: {e}")
    
    def _encrypt(self, data: str) -> str:
        """Encrypt data"""
        if not self._fernet:
            return data
        try:
            return self._fernet.encrypt(data.encode()).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return data
    
    def _decrypt(self, data: str) -> str:
        """Decrypt data"""
        if not self._fernet:
            return data
        try:
            return self._fernet.decrypt(data.encode()).decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return data
    
    def store_credential(self, marketplace_id: str, credential_type: str, credentials: Dict[str, Any]) -> bool:
        """Store encrypted credentials"""
        try:
            if marketplace_id not in self._credentials:
                self._credentials[marketplace_id] = {}
            
            serialized = json.dumps(credentials)
            encrypted = self._encrypt(serialized)
            
            self._credentials[marketplace_id][credential_type] = {
                "data": encrypted,
                "encrypted": self._fernet is not None,
                "stored_at": datetime.now().isoformat()
            }
            
            logger.info(f"Credentials stored for {marketplace_id}/{credential_type}")
            return True
        except Exception as e:
            logger.error(f"Failed to store credentials: {e}")
            return False
    
    def get_credential(self, marketplace_id: str, credential_type: str) -> Optional[Dict[str, Any]]:
        """Retrieve and decrypt credentials"""
        try:
            marketplace_creds = self._credentials.get(marketplace_id, {})
            cred_data = marketplace_creds.get(credential_type)
            
            if not cred_data:
                return None
            
            decrypted = self._decrypt(cred_data["data"])
            return json.loads(decrypted)
        except Exception as e:
            logger.error(f"Failed to get credentials: {e}")
            return None
    
    def delete_credential(self, marketplace_id: str, credential_type: str) -> bool:
        """Delete stored credentials"""
        try:
            if marketplace_id in self._credentials:
                if credential_type in self._credentials[marketplace_id]:
                    del self._credentials[marketplace_id][credential_type]
                    logger.info(f"Credentials deleted for {marketplace_id}/{credential_type}")
                    return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete credentials: {e}")
            return False
    
    def rotate_credential(self, marketplace_id: str, credential_type: str, new_credentials: Dict[str, Any]) -> bool:
        """Rotate credentials"""
        try:
            self.delete_credential(marketplace_id, credential_type)
            return self.store_credential(marketplace_id, credential_type, new_credentials)
        except Exception as e:
            logger.error(f"Failed to rotate credentials: {e}")
            return False
    
    def list_credential_types(self, marketplace_id: str) -> List[str]:
        """List credential types for marketplace"""
        return list(self._credentials.get(marketplace_id, {}).keys())
    
    def has_credentials(self, marketplace_id: str, credential_type: str) -> bool:
        """Check if credentials exist"""
        marketplace_creds = self._credentials.get(marketplace_id, {})
        return credential_type in marketplace_creds


def main():
    """Test credential manager"""
    manager = CredentialManager("test-encryption-key-1234567890123456789012")
    
    # Test store
    success = manager.store_credential("test-marketplace", "api_key", {"key": "secret123", "secret": "secret456"})
    print(f"Store: {success}")
    
    # Test retrieve
    creds = manager.get_credential("test-marketplace", "api_key")
    print(f"Retrieve: {creds}")
    
    # Test rotate
    success = manager.rotate_credential("test-marketplace", "api_key", {"key": "newkey", "secret": "newsecret"})
    print(f"Rotate: {success}")
    
    # Test delete
    success = manager.delete_credential("test-marketplace", "api_key")
    print(f"Delete: {success}")


if __name__ == "__main__":
    main()
