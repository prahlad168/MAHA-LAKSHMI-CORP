# MAHA SALES ENGINE V1 - Webhook Gateway Documentation

## Overview

Webhook receiving, validation, routing, and replay protection.

## Features

- Signature validation
- Replay protection
- Idempotency
- Provider routing
- Automatic retries
- Dead letter support

## Usage

```python
from webhooks.gateway import WebhookGateway

gateway = WebhookGateway(db, event_bus)

# Register route
gateway.register_route(
    marketplace_id="gumroad",
    event_types=["sale", "refund"],
    secret="webhook-secret",
    handler=handle_event
)

# Process webhook
result = await gateway.process_webhook(
    marketplace_id="gumroad",
    payload={"event_type": "sale", "id": "evt-123"},
    signature="hmac-signature"
)
```

## Security

- HMAC signature validation
- Replay attack prevention
- Event deduplication