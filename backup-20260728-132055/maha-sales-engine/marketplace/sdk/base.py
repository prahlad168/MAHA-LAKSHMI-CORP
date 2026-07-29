#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Marketplace Plugin SDK
Base classes and interfaces for marketplace provider plugins.
"""

import os
import sys
import json
import logging
import importlib
import inspect
from pathlib import Path
from typing import Dict, Any, Optional, List, Type
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.marketplace.sdk")


# ============ ENUMS ============

class PublicationStatus(Enum):
    DRAFT = "draft"
    PREPARING = "preparing"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    UPDATING = "updating"
    ARCHIVED = "archived"
    DELETED = "deleted"
    SYNCING = "syncing"
    FAILED = "failed"
    RETRYING = "retrying"


class MarketplaceStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class AuthType(Enum):
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    JWT = "jwt"
    BASIC = "basic"
    CUSTOM = "custom"


class JobPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class JobState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    WAITING = "waiting"
    RETRY = "retry"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


# ============ DATA MODELS ============

@dataclass
class MarketplaceConfig:
    """Marketplace configuration"""
    marketplace_id: str
    name: str
    provider: str
    version: str
    status: str
    capabilities: List[str]
    auth_type: str
    config: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""


@dataclass
class ProductMapping:
    """Product to marketplace mapping"""
    mapping_id: str
    product_id: str
    marketplace_id: str
    marketplace_product_id: Optional[str] = None
    listing_id: Optional[str] = None
    external_url: Optional[str] = None
    published_version: Optional[str] = None
    publication_status: str = PublicationStatus.DRAFT.value
    last_sync: Optional[str] = None
    last_error: Optional[str] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PublicationJob:
    """Publication job"""
    job_id: str
    marketplace_id: str
    product_id: str
    action: str
    priority: str
    state: str
    parameters: Dict[str, Any]
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    retry_count: int = 0
    max_retries: int = 3


# ============ BASE PROVIDER INTERFACE ============

class BaseMarketplaceProvider(ABC):
    """
    Base class for all marketplace providers.
    Every provider MUST implement all abstract methods.
    """
    
    # Provider metadata
    PROVIDER_NAME: str = ""
    PROVIDER_VERSION: str = "1.0.0"
    CAPABILITIES: List[str] = []
    AUTH_TYPE: str = AuthType.API_KEY.value
    
    def __init__(self, config: Dict[str, Any], credential_manager):
        self.config = config
        self.credential_manager = credential_manager
        self.marketplace_id = config.get("marketplace_id", "")
        self.logger = logging.getLogger(f"maha-sales-engine.marketplace.provider.{self.PROVIDER_NAME}")
        self._initialized = False
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize provider connection and validate configuration"""
        pass
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with marketplace using stored credentials"""
        pass
    
    @abstractmethod
    async def validate(self) -> Dict[str, Any]:
        """Validate provider configuration and credentials"""
        pass
    
    @abstractmethod
    async def publish(self, product_id: str, product_data: Dict[str, Any], mapping: ProductMapping) -> Dict[str, Any]:
        """Publish product to marketplace"""
        pass
    
    @abstractmethod
    async def update(self, product_id: str, product_data: Dict[str, Any], mapping: ProductMapping) -> Dict[str, Any]:
        """Update existing product listing"""
        pass
    
    @abstractmethod
    async def archive(self, mapping: ProductMapping) -> Dict[str, Any]:
        """Archive product listing"""
        pass
    
    @abstractmethod
    async def delete(self, mapping: ProductMapping) -> Dict[str, Any]:
        """Delete product listing"""
        pass
    
    @abstractmethod
    async def sync(self, mapping: ProductMapping) -> Dict[str, Any]:
        """Synchronize product data with marketplace"""
        pass
    
    @abstractmethod
    async def health(self) -> Dict[str, Any]:
        """Check provider health and connectivity"""
        pass
    
    @abstractmethod
    def capabilities(self) -> List[str]:
        """Return list of provider capabilities"""
        pass
    
    @abstractmethod
    async def shutdown(self) -> bool:
        """Cleanup and shutdown provider"""
        pass
    
    def _log(self, level: str, message: str, **kwargs):
        """Log with marketplace context"""
        getattr(self.logger, level)(f"[{self.marketplace_id}] {message}", extra=kwargs)


# ============ PROVIDER REGISTRY ============

class ProviderRegistry:
    """Registry for marketplace providers"""
    
    def __init__(self):
        self._providers: Dict[str, Type[BaseMarketplaceProvider]] = {}
        self._instances: Dict[str, BaseMarketplaceProvider] = {}
        self._capabilities: Dict[str, List[str]] = {}
    
    def register(self, provider_class: Type[BaseMarketplaceProvider]) -> bool:
        """Register a provider class"""
        try:
            provider_name = provider_class.PROVIDER_NAME
            if not provider_name:
                raise ValueError("Provider must have PROVIDER_NAME defined")
            
            self._providers[provider_name] = provider_class
            self._capabilities[provider_name] = provider_class.CAPABILITIES
            
            logger.info(f"Provider registered: {provider_name} v{provider_class.PROVIDER_VERSION}")
            return True
        except Exception as e:
            logger.error(f"Failed to register provider {provider_class.__name__}: {e}")
            return False
    
    def unregister(self, provider_name: str) -> bool:
        """Unregister a provider"""
        if provider_name in self._providers:
            del self._providers[provider_name]
            del self._capabilities[provider_name]
            if provider_name in self._instances:
                del self._instances[provider_name]
            logger.info(f"Provider unregistered: {provider_name}")
            return True
        return False
    
    def get_provider_class(self, provider_name: str) -> Optional[Type[BaseMarketplaceProvider]]:
        """Get provider class by name"""
        return self._providers.get(provider_name)
    
    def get_registered_providers(self) -> List[str]:
        """Get list of registered provider names"""
        return list(self._providers.keys())
    
    def get_capabilities(self, provider_name: str) -> List[str]:
        """Get capabilities for a provider"""
        return self._capabilities.get(provider_name, [])
    
    def has_capability(self, provider_name: str, capability: str) -> bool:
        """Check if provider has specific capability"""
        return capability in self._capabilities.get(provider_name, [])
    
    def create_instance(self, provider_name: str, config: Dict[str, Any], credential_manager) -> Optional[BaseMarketplaceProvider]:
        """Create provider instance"""
        provider_class = self._providers.get(provider_name)
        if not provider_class:
            logger.error(f"Provider not found: {provider_name}")
            return None
        
        try:
            instance = provider_class(config, credential_manager)
            self._instances[provider_name] = instance
            return instance
        except Exception as e:
            logger.error(f"Failed to create provider instance {provider_name}: {e}")
            return None
    
    def get_instance(self, provider_name: str) -> Optional[BaseMarketplaceProvider]:
        """Get existing provider instance"""
        return self._instances.get(provider_name)


# ============ PROVIDER LOADER ============

class ProviderLoader:
    """Automatic provider discovery and loading"""
    
    def __init__(self, registry: ProviderRegistry, providers_dir: Path):
        self.registry = registry
        self.providers_dir = providers_dir
        self._loaded_modules = set()
    
    def discover_providers(self) -> List[str]:
        """Discover all provider modules"""
        discovered = []
        
        if not self.providers_dir.exists():
            return discovered
        
        for file_path in self.providers_dir.rglob("*.py"):
            if file_path.name.startswith("_"):
                continue
            
            module_name = file_path.stem
            discovered.append(module_name)
        
        return discovered
    
    def load_provider(self, module_name: str) -> Optional[Type[BaseMarketplaceProvider]]:
        """Load a provider module"""
        try:
            # Add providers directory to path
            if str(self.providers_dir) not in sys.path:
                sys.path.insert(0, str(self.providers_dir))
            
            module = importlib.import_module(module_name)
            
            # Find provider class
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BaseMarketplaceProvider) and 
                    obj != BaseMarketplaceProvider):
                    return obj
            
            return None
        except Exception as e:
            logger.error(f"Failed to load provider {module_name}: {e}")
            return None
    
    def load_all_providers(self) -> int:
        """Discover and load all providers"""
        discovered = self.discover_providers()
        loaded_count = 0
        
        for module_name in discovered:
            if module_name in self._loaded_modules:
                continue
            
            provider_class = self.load_provider(module_name)
            if provider_class:
                if self.registry.register(provider_class):
                    self._loaded_modules.add(module_name)
                    loaded_count += 1
        
        logger.info(f"Loaded {loaded_count} providers from {self.providers_dir}")
        return loaded_count
    
    def validate_provider(self, provider_class: Type[BaseMarketplaceProvider]) -> Dict[str, Any]:
        """Validate provider implementation"""
        errors = []
        warnings = []
        
        # Check required attributes
        if not hasattr(provider_class, "PROVIDER_NAME") or not provider_class.PROVIDER_NAME:
            errors.append("Missing PROVIDER_NAME")
        
        if not hasattr(provider_class, "PROVIDER_VERSION") or not provider_class.PROVIDER_VERSION:
            warnings.append("Missing PROVIDER_VERSION")
        
        if not hasattr(provider_class, "CAPABILITIES") or not isinstance(provider_class.CAPABILITIES, list):
            errors.append("Missing or invalid CAPABILITIES")
        
        # Check required methods
        required_methods = [
            "initialize", "authenticate", "validate", "publish", "update",
            "archive", "delete", "sync", "health", "capabilities", "shutdown"
        ]
        
        for method in required_methods:
            if not hasattr(provider_class, method):
                errors.append(f"Missing method: {method}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }


# ============ CREDENTIAL MANAGER ============

class CredentialManager:
    """Secure credential management with encryption support"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        self.encryption_key = encryption_key or os.environ.get("MARKETPLACE_ENCRYPTION_KEY", "")
        self._credentials: Dict[str, Dict[str, Any]] = {}
    
    def store_credential(self, marketplace_id: str, credential_type: str, credentials: Dict[str, Any]) -> bool:
        """Store encrypted credentials"""
        try:
            if marketplace_id not in self._credentials:
                self._credentials[marketplace_id] = {}
            
            self._credentials[marketplace_id][credential_type] = {
                "data": credentials,
                "encrypted": bool(self.encryption_key),
                "stored_at": ""
            }
            self._credentials[marketplace_id][credential_type]["stored_at"] = ""
            
            logger.info(f"Credentials stored for {marketplace_id}/{credential_type}")
            return True
        except Exception as e:
            logger.error(f"Failed to store credentials: {e}")
            return False
    
    def get_credential(self, marketplace_id: str, credential_type: str) -> Optional[Dict[str, Any]]:
        """Retrieve credentials"""
        try:
            marketplace_creds = self._credentials.get(marketplace_id, {})
            cred_data = marketplace_creds.get(credential_type)
            
            if cred_data:
                return cred_data.get("data")
            return None
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


# ============ STATE MACHINE ============

class PublicationStateMachine:
    """State machine for publication status transitions"""
    
    VALID_TRANSITIONS = {
        PublicationStatus.DRAFT.value: [
            PublicationStatus.PREPARING.value,
            PublicationStatus.PUBLISHING.value
        ],
        PublicationStatus.PREPARING.value: [
            PublicationStatus.PUBLISHING.value,
            PublicationStatus.DRAFT.value,
            PublicationStatus.FAILED.value
        ],
        PublicationStatus.PUBLISHING.value: [
            PublicationStatus.PUBLISHED.value,
            PublicationStatus.FAILED.value,
            PublicationStatus.RETRYING.value
        ],
        PublicationStatus.PUBLISHED.value: [
            PublicationStatus.UPDATING.value,
            PublicationStatus.ARCHIVED.value,
            PublicationStatus.SYNCING.value
        ],
        PublicationStatus.UPDATING.value: [
            PublicationStatus.PUBLISHED.value,
            PublicationStatus.FAILED.value,
            PublicationStatus.RETRYING.value
        ],
        PublicationStatus.ARCHIVED.value: [
            PublicationStatus.PUBLISHING.value,
            PublicationStatus.DELETED.value
        ],
        PublicationStatus.DELETED.value: [],
        PublicationStatus.SYNCING.value: [
            PublicationStatus.PUBLISHED.value,
            PublicationStatus.FAILED.value
        ],
        PublicationStatus.FAILED.value: [
            PublicationStatus.RETRYING.value,
            PublicationStatus.PREPARING.value,
            PublicationStatus.DRAFT.value
        ],
        PublicationStatus.RETRYING.value: [
            PublicationStatus.PUBLISHING.value,
            PublicationStatus.FAILED.value,
            PublicationStatus.DRAFT.value
        ]
    }
    
    @classmethod
    def can_transition(cls, from_status: str, to_status: str) -> bool:
        """Check if transition is valid"""
        valid_targets = cls.VALID_TRANSITIONS.get(from_status, [])
        return to_status in valid_targets
    
    @classmethod
    def get_valid_transitions(cls, from_status: str) -> List[str]:
        """Get valid target statuses"""
        return cls.VALID_TRANSITIONS.get(from_status, [])
    
    @classmethod
    def transition(cls, from_status: str, to_status: str) -> bool:
        """Attempt state transition"""
        if cls.can_transition(from_status, to_status):
            logger.info(f"State transition: {from_status} -> {to_status}")
            return True
        logger.warning(f"Invalid state transition: {from_status} -> {to_status}")
        return False


# ============ EVENT BUS ============

class Event:
    """Event data structure"""
    
    def __init__(self, event_type: str, data: Dict[str, Any], source: str = "marketplace"):
        self.event_type = event_type
        self.data = data
        self.source = source
        self.timestamp = ""
        self.event_id = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "source": self.source,
            "timestamp": self.timestamp,
            "data": self.data
        }


class EventBus:
    """Internal event system for marketplace operations"""
    
    def __init__(self):
        self._handlers: Dict[str, List[callable]] = {}
        self._event_history: List[Event] = []
        self._max_history = 1000
    
    def subscribe(self, event_type: str, handler: callable):
        """Subscribe to event type"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.debug(f"Handler subscribed to {event_type}")
    
    def unsubscribe(self, event_type: str, handler: callable):
        """Unsubscribe from event type"""
        if event_type in self._handlers:
            self._handlers[event_type] = [h for h in self._handlers[event_type] if h != handler]
    
    def publish(self, event: Event) -> bool:
        """Publish event to all subscribers"""
        try:
            event.timestamp = ""
            event.event_id = ""
            
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history.pop(0)
            
            handlers = self._handlers.get(event.event_type, [])
            for handler in handlers:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Event handler failed for {event.event_type}: {e}")
            
            logger.debug(f"Event published: {event.event_type}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            return False
    
    def get_history(self, event_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get event history"""
        events = self._event_history
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        return [e.to_dict() for e in events[-limit:]]


# ============ AUDIT LOGGER ============

class AuditLogger:
    """Audit logging for marketplace operations"""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def log(self, action: str, marketplace_id: str, product_id: Optional[str], 
            before: Optional[Dict] = None, after: Optional[Dict] = None,
            ip_address: str = "", result: str = "success", user_id: str = "system"):
        """Log audit event"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO marketplace_audit_log (
                    id, action, marketplace_id, product_id, before_data, after_data,
                    ip_address, result, user_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"AUD-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                action,
                marketplace_id,
                product_id,
                json.dumps(before) if before else None,
                json.dumps(after) if after else None,
                ip_address,
                result,
                user_id,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            logger.debug(f"Audit log: {action} on {marketplace_id}")
            
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")


# Global event bus instance
event_bus = EventBus()
