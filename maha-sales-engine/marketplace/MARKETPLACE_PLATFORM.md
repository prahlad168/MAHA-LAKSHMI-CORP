# MAHA SALES ENGINE V1 - Marketplace Platform

## Overview

The Marketplace Platform provides a unified interface for publishing digital products to any supported marketplace without modifying the core application.

## Architecture

```
Marketplace Platform
├── Plugin SDK (Base interfaces)
├── Provider Registry (Discovery & loading)
├── Credential Manager (Secure storage)
├── State Machine (Publication status)
├── Event Bus (Async events)
├── Job Queue (Async processing)
├── Publishing Engine (Publish/Update/Archive/Delete)
├── Synchronization Engine (Sync products)
├── Webhook Engine (Incoming webhooks)
├── Audit Logger (Compliance)
└── REST API (Endpoints)
```

## Plugin SDK

Every marketplace provider must implement `BaseMarketplaceProvider`:

```python
class MyProvider(BaseMarketplaceProvider):
    PROVIDER_NAME = "my_marketplace"
    PROVIDER_VERSION = "1.0.0"
    CAPABILITIES = ["supports_publish", "supports_update"]
    AUTH_TYPE = "api_key"
    
    async def initialize(self) -> bool: ...
    async def authenticate(self) -> bool: ...
    async def validate(self) -> Dict: ...
    async def publish(self, product_id, product_data, mapping) -> Dict: ...
    async def update(self, product_id, product_data, mapping) -> Dict: ...
    async def archive(self, mapping) -> Dict: ...
    async def delete(self, mapping) -> Dict: ...
    async def sync(self, mapping) -> Dict: ...
    async def health(self) -> Dict: ...
    def capabilities(self) -> List[str]: ...
    async def shutdown(self) -> bool: ...
```

## Supported Providers

| Provider | Status | Capabilities |
|----------|--------|--------------|
| Gumroad | Skeleton | publish, update, delete, archive, variants, preview |
| Etsy | Skeleton | publish, update, delete, archive, tags, categories |
| Payhip | Skeleton | publish, update, delete, archive, variants, discounts |
| Lemon Squeezy | Skeleton | publish, update, delete, archive, variants, license keys |
| Creative Market | Skeleton | publish, update, delete, archive, variants, preview |
| Ko-fi | Skeleton | publish, update, delete, archive, variants, preview |
| Shopify | Skeleton | publish, update, delete, archive, variants, discounts |
| Sellfy | Skeleton | publish, update, delete, archive, variants, discounts |
| WooCommerce | Skeleton | publish, update, delete, archive, variants, custom metadata |
| Custom | Template | All capabilities |

## Publication Lifecycle

```
Draft → Preparing → Publishing → Published → Updating/Archived/Syncing
                    ↓                ↓
                  Failed ←←←←←←←←←←←←←←←←←
                    ↓
                  Retrying
```

## REST API

### Marketplaces
- `POST /api/v1/marketplaces` - Register marketplace
- `GET /api/v1/marketplaces` - List marketplaces
- `GET /api/v1/marketplaces/{id}` - Get marketplace
- `DELETE /api/v1/marketplaces/{id}` - Remove marketplace

### Providers
- `GET /api/v1/providers` - List providers
- `GET /api/v1/providers/{name}/health` - Provider health
- `POST /api/v1/providers/{name}/validate` - Validate provider

### Credentials
- `POST /api/v1/credentials` - Store credentials
- `GET /api/v1/credentials/{id}` - Get credentials
- `DELETE /api/v1/credentials/{id}` - Delete credentials

### Publication
- `POST /api/v1/publish` - Publish product
- `POST /api/v1/update` - Update product
- `POST /api/v1/archive` - Archive product
- `POST /api/v1/delete` - Delete product

### Synchronization
- `POST /api/v1/sync/product` - Sync single product
- `POST /api/v1/sync/marketplace/{id}` - Sync marketplace

### Jobs
- `GET /api/v1/jobs/{id}` - Get job status
- `POST /api/v1/jobs/{id}/cancel` - Cancel job
- `GET /api/v1/jobs/queue/stats` - Queue stats

### Webhooks
- `POST /api/v1/webhooks/{id}` - Receive webhook
- `POST /api/v1/webhooks/{id}/register` - Register webhook

## Event Bus

Events:
- `marketplace.registered`
- `marketplace.removed`
- `publish.started`
- `publish.completed`
- `publish.failed`
- `update.started`
- `update.completed`
- `archive.completed`
- `delete.completed`
- `sync.started`
- `sync.completed`
- `sync.failed`
- `webhook.received`
- `webhook.processed`
- `webhook.failed`
- `retry.started`
- `retry.completed`
- `retry.failed`

## Database

12 tables with indexes for performance.

## Security

- Credential encryption (Fernet)
- Secret rotation support
- Least privilege
- Input validation
- Webhook signature validation

## Next Steps

- Phase 5: AI Marketing Engine
- Phase 6: Sales Analytics
- Phase 7: Payment Settlement