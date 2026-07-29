# MAHA SALES ENGINE V1 - Marketplace Platform

Plugin-based marketplace integration platform for publishing digital products to multiple marketplaces.

## Purpose

Provides unified interface for publishing products to any supported marketplace without modifying core application.

## Quick Start

```python
from core.registry import ProviderRegistry, ProviderLoader
from security.credentials import CredentialManager
from engines.publishing import PublishingEngine
from events.bus import event_bus

# Initialize
registry = ProviderRegistry()
loader = ProviderLoader(registry, Path("marketplace/providers"))
loader.load_all_providers()

credential_manager = CredentialManager()
publishing_engine = PublishingEngine(db, registry, credential_manager, event_bus)

# Publish
result = await publishing_engine.publish("gumroad", "ML-20260727-000001", product_data)
```

## Supported Providers

- Gumroad
- Etsy
- Payhip
- Lemon Squeezy
- Creative Market
- Ko-fi
- Shopify
- Sellfy
- WooCommerce
- Custom

## Documentation

- [MARKETPLACE_PLATFORM.md](MARKETPLACE_PLATFORM.md) - Main documentation
- [PLUGIN_SDK.md](PLUGIN_SDK.md) - SDK guide
- [EVENT_BUS.md](EVENT_BUS.md) - Event system
- [JOB_QUEUE.md](JOB_QUEUE.md) - Job queue
- [STATE_MACHINE.md](STATE_MACHINE.md) - State machine

## API

Start API server:
```bash
python -m marketplace.api.routes
```

API docs: http://localhost:8002/api/docs

## Status

| Component | Status |
|-----------|--------|
| Plugin SDK | ✅ |
| Provider Registry | ✅ |
| Credential Manager | ✅ |
| State Machine | ✅ |
| Event Bus | ✅ |
| Job Queue | ✅ |
| Publishing Engine | ✅ |
| Sync Engine | ✅ |
| Webhook Engine | ✅ |
| REST API | ✅ |
| Providers | ✅ Skeletons |
| Tests | ✅ |
| Documentation | ✅ |
