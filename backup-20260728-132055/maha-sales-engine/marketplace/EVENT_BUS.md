# MAHA SALES ENGINE V1 - Event Bus Documentation

## Overview

The Event Bus provides asynchronous, decoupled communication between marketplace components.

## Architecture

```
Publisher → Event Bus → Subscribers
                ↓
         Middleware (optional)
                ↓
         Event History
```

## Usage

```python
from events.bus import event_bus, MarketplaceEvents

# Subscribe
def handle_publish(event):
    print(f"Publishing: {event.data}")

event_bus.subscribe(MarketplaceEvents.PUBLISH_STARTED, handle_publish)

# Publish
event = Event(MarketplaceEvents.PUBLISH_STARTED, {
    "marketplace_id": "mkt-123",
    "product_id": "prod-456"
})
event_bus.publish(event)

# Unsubscribe
event_bus.unsubscribe(MarketplaceEvents.PUBLISH_STARTED, handle_publish)
```

## Events

All events include:
- `event_id`: Unique identifier
- `event_type`: Type of event
- `source`: Event source
- `timestamp`: ISO timestamp
- `data`: Event payload

## Event History

```python
# Get all events
history = event_bus.get_history()

# Filter by type
publish_events = event_bus.get_history(event_type=MarketplaceEvents.PUBLISH_STARTED)

# Limit results
recent = event_bus.get_history(limit=50)
```

## Middleware

```python
def auth_middleware(event):
    if event.data.get("requires_auth"):
        # Validate auth
        pass
    return True

event_bus.add_middleware(auth_middleware)
```

## Best Practices

1. Use specific event types
2. Include relevant context in data
3. Handle exceptions in handlers
4. Don't block handlers
5. Use middleware for cross-cutting concerns