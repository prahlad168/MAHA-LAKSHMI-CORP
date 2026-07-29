# MAHA SALES ENGINE V1 - Marketplace Connector

Production-ready marketplace connector for publishing digital products to Gumroad.

## Features

- Multi-account marketplace management
- Automated product publication pipeline
- Package validation engine
- Webhook processing with signature verification
- Retry engine with exponential backoff
- Synchronization engine
- Health monitoring and metrics
- Audit logging
- REST API with 15+ endpoints

## Quick Start

```python
from marketplace_connector.providers.gumroad.gumroad_provider import GumroadProvider
from marketplace_connector.publication.publication_pipeline import PublicationPipeline
from marketplace_connector.publication.validation_engine import ValidationEngine

# Initialize provider
provider = GumroadProvider({"api_key": "your-api-key"})

# Create pipeline
validation_engine = ValidationEngine()
pipeline = PublicationPipeline(provider, validation_engine, db_manager)

# Publish product
result = await pipeline.execute("/path/to/product/package", metadata)
print(result.marketplace_url)
```

## Architecture

```
marketplace_connector/
├── core/                    # Base interfaces and types
├── providers/               # Marketplace implementations
│   └── gumroad/            # Gumroad provider
├── publication/             # Publication pipeline and validation
├── sync/                    # Synchronization engine
├── webhooks/                # Webhook processing
├── queue/                   # Retry and publication queue
├── health/                  # Health monitoring
├── audit/                   # Audit logging
├── metrics/                 # Metrics collection
├── api/                     # REST API routes
├── db/                      # Database schema and manager
└── tests/                   # Test suite
```

## Documentation

- [Gumroad Connector](GUMROAD_CONNECTOR.md)
- [Publication Pipeline](PUBLICATION_PIPELINE.md)
- [Webhooks](WEBHOOKS.md)
- [Sync Engine](SYNC_ENGINE.md)
- [Database Schema](DATABASE_SCHEMA.md)
- [API Reference](API_REFERENCE.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Troubleshooting](TROUBLESHOOTING.md)
