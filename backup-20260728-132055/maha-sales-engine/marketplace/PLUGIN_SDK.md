# MAHA SALES ENGINE V1 - Plugin SDK Guide

## Overview

The Plugin SDK enables third-party developers to create marketplace provider plugins without modifying core application code.

## Creating a Provider

1. Inherit from `BaseMarketplaceProvider`
2. Implement all abstract methods
3. Define provider metadata
4. Place in `marketplace/providers/` directory

## Provider Interface

```python
class BaseMarketplaceProvider(ABC):
    PROVIDER_NAME: str
    PROVIDER_VERSION: str
    CAPABILITIES: List[str]
    AUTH_TYPE: str
    
    async def initialize(self) -> bool
    async def authenticate(self) -> bool
    async def validate(self) -> Dict[str, Any]
    async def publish(self, product_id, product_data, mapping) -> Dict[str, Any]
    async def update(self, product_id, product_data, mapping) -> Dict[str, Any]
    async def archive(self, mapping) -> Dict[str, Any]
    async def delete(self, mapping) -> Dict[str, Any]
    async def sync(self, mapping) -> Dict[str, Any]
    async def health(self) -> Dict[str, Any]
    def capabilities(self) -> List[str]
    async def shutdown(self) -> bool
```

## Capabilities

Providers declare capabilities:
- `supports_publish`
- `supports_update`
- `supports_delete`
- `supports_archive`
- `supports_variants`
- `supports_preview`
- `supports_tags`
- `supports_categories`
- `supports_discounts`
- `supports_license_keys`
- `supports_custom_metadata`

## Authentication Types

- `api_key` - Simple API key
- `oauth2` - OAuth 2.0
- `jwt` - JWT tokens
- `basic` - Basic auth
- `custom` - Custom auth

## Best Practices

1. Never access internal database directly
2. Use provided interfaces only
3. Implement proper error handling
4. Log all operations
5. Support async operations
6. Return structured responses
7. Validate all inputs
8. Handle rate limiting

## Validation

Providers are validated on registration:
- Required attributes present
- Required methods implemented
- Inheritance correct
- Capabilities declared

## Example

See `providers/custom.py` for a complete example.