#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Marketplace Registry
Provider registry and discovery system.
"""

import os
import sys
import json
import importlib
import inspect
from pathlib import Path
from typing import Dict, Any, Optional, List, Type
from sdk.base import BaseMarketplaceProvider, AuthType

logger = logging.getLogger("maha-sales-engine.marketplace.registry")


class ProviderCapability:
    """Provider capability descriptor"""
    
    def __init__(self, name: str, description: str, supported: bool = True):
        self.name = name
        self.description = description
        self.supported = supported


class ProviderMetadata:
    """Provider metadata"""
    
    def __init__(self, provider_class: Type[BaseMarketplaceProvider]):
        self.name = provider_class.PROVIDER_NAME
        self.version = provider_class.PROVIDER_VERSION
        self.auth_type = provider_class.AUTH_TYPE
        self.capabilities = provider_class.CAPABILITIES
        self.class_name = provider_class.__name__
        self.module = provider_class.__module__


class ProviderRegistry:
    """Central registry for marketplace providers"""
    
    def __init__(self):
        self._providers: Dict[str, Type[BaseMarketplaceProvider]] = {}
        self._metadata: Dict[str, ProviderMetadata] = {}
        self._instances: Dict[str, BaseMarketplaceProvider] = {}
        self._loading_lock = False
    
    def register(self, provider_class: Type[BaseMarketplaceProvider]) -> bool:
        """Register a provider class"""
        try:
            if self._loading_lock:
                return False
            
            metadata = ProviderMetadata(provider_class)
            
            if metadata.name in self._providers:
                logger.warning(f"Provider {metadata.name} already registered, skipping")
                return False
            
            self._providers[metadata.name] = provider_class
            self._metadata[metadata.name] = metadata
            
            logger.info(f"Registered provider: {metadata.name} v{metadata.version}")
            return True
        except Exception as e:
            logger.error(f"Failed to register provider {provider_class.__name__}: {e}")
            return False
    
    def unregister(self, provider_name: str) -> bool:
        """Unregister a provider"""
        if provider_name not in self._providers:
            return False
        
        try:
            # Shutdown instance if exists
            if provider_name in self._instances:
                instance = self._instances[provider_name]
                if hasattr(instance, 'shutdown'):
                    import asyncio
                    asyncio.run(instance.shutdown())
                del self._instances[provider_name]
            
            del self._providers[provider_name]
            del self._metadata[provider_name]
            
            logger.info(f"Unregistered provider: {provider_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to unregister provider {provider_name}: {e}")
            return False
    
    def get_provider_class(self, provider_name: str) -> Optional[Type[BaseMarketplaceProvider]]:
        """Get provider class by name"""
        return self._providers.get(provider_name)
    
    def get_metadata(self, provider_name: str) -> Optional[ProviderMetadata]:
        """Get provider metadata"""
        return self._metadata.get(provider_name)
    
    def list_providers(self) -> List[Dict[str, Any]]:
        """List all registered providers"""
        result = []
        for name, metadata in self._metadata.items():
            result.append({
                "name": metadata.name,
                "version": metadata.version,
                "auth_type": metadata.auth_type,
                "capabilities": metadata.capabilities,
                "class_name": metadata.class_name,
                "module": metadata.module
            })
        return result
    
    def get_capabilities(self, provider_name: str) -> List[str]:
        """Get capabilities for a provider"""
        metadata = self._metadata.get(provider_name)
        return metadata.capabilities if metadata else []
    
    def has_capability(self, provider_name: str, capability: str) -> bool:
        """Check if provider supports capability"""
        capabilities = self.get_capabilities(provider_name)
        return capability in capabilities
    
    def create_instance(self, provider_name: str, config: Dict[str, Any], credential_manager) -> Optional[BaseMarketplaceProvider]:
        """Create provider instance"""
        provider_class = self._providers.get(provider_name)
        if not provider_class:
            logger.error(f"Provider not found: {provider_name}")
            return None
        
        try:
            instance = provider_class(config, credential_manager)
            self._instances[provider_name] = instance
            logger.info(f"Created instance: {provider_name}")
            return instance
        except Exception as e:
            logger.error(f"Failed to create instance {provider_name}: {e}")
            return None
    
    def get_instance(self, provider_name: str) -> Optional[BaseMarketplaceProvider]:
        """Get existing provider instance"""
        return self._instances.get(provider_name)
    
    def get_all_instances(self) -> Dict[str, BaseMarketplaceProvider]:
        """Get all provider instances"""
        return dict(self._instances)
    
    def validate_dependencies(self, provider_name: str) -> Dict[str, Any]:
        """Validate provider dependencies"""
        provider_class = self._providers.get(provider_name)
        if not provider_class:
            return {"valid": False, "errors": [f"Provider {provider_name} not found"]}
        
        errors = []
        warnings = []
        
        # Check base class
        if not issubclass(provider_class, BaseMarketplaceProvider):
            errors.append("Provider must inherit from BaseMarketplaceProvider")
        
        # Check required attributes
        if not hasattr(provider_class, "PROVIDER_NAME"):
            errors.append("Missing PROVIDER_NAME")
        if not hasattr(provider_class, "PROVIDER_VERSION"):
            warnings.append("Missing PROVIDER_VERSION")
        if not hasattr(provider_class, "CAPABILITIES"):
            errors.append("Missing CAPABILITIES")
        if not hasattr(provider_class, "AUTH_TYPE"):
            warnings.append("Missing AUTH_TYPE, defaulting to api_key")
        
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
    
    def get_providers_by_capability(self, capability: str) -> List[str]:
        """Get all providers that support a capability"""
        result = []
        for name, metadata in self._metadata.items():
            if capability in metadata.capabilities:
                result.append(name)
        return result


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
            logger.warning(f"Providers directory not found: {self.providers_dir}")
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
            # Add providers directory to path if not already
            providers_parent = str(self.providers_dir.parent)
            if providers_parent not in sys.path:
                sys.path.insert(0, providers_parent)
            
            # Import module
            module = importlib.import_module(f"marketplace.providers.{module_name}")
            
            # Find provider class
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BaseMarketplaceProvider) and 
                    obj != BaseMarketplaceProvider):
                    return obj
            
            logger.warning(f"No provider class found in {module_name}")
            return None
        except Exception as e:
            logger.error(f"Failed to load provider {module_name}: {e}")
            return None
    
    def load_all_providers(self) -> Dict[str, Any]:
        """Discover and load all providers"""
        discovered = self.discover_providers()
        results = {
            "loaded": 0,
            "failed": 0,
            "providers": []
        }
        
        for module_name in discovered:
            if module_name in self._loaded_modules:
                continue
            
            provider_class = self.load_provider(module_name)
            if provider_class:
                # Validate before registering
                validation = self.registry.validate_dependencies(provider_class.PROVIDER_NAME)
                
                if validation["valid"]:
                    if self.registry.register(provider_class):
                        self._loaded_modules.add(module_name)
                        results["loaded"] += 1
                        results["providers"].append(provider_class.PROVIDER_NAME)
                else:
                    results["failed"] += 1
                    logger.error(f"Provider validation failed for {module_name}: {validation['errors']}")
        
        logger.info(f"Provider loading complete: {results['loaded']} loaded, {results['failed']} failed")
        return results
    
    def validate_provider(self, provider_class: Type[BaseMarketplaceProvider]) -> Dict[str, Any]:
        """Validate provider implementation"""
        return self.registry.validate_dependencies(provider_class.PROVIDER_NAME)


def main():
    """Test registry and loader"""
    from pathlib import Path
    
    registry = ProviderRegistry()
    providers_dir = Path(__file__).parent.parent / "providers"
    loader = ProviderLoader(registry, providers_dir)
    
    # Discover providers
    discovered = loader.discover_providers()
    print(f"Discovered providers: {discovered}")
    
    # Load all
    results = loader.load_all_providers()
    print(f"Load results: {results}")
    
    # List registered
    providers = registry.list_providers()
    print(f"Registered providers: {len(providers)}")
    for p in providers:
        print(f"  - {p['name']} v{p['version']}")


if __name__ == "__main__":
    main()
