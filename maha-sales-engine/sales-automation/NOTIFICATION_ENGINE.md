# MAHA SALES ENGINE V1 - Notification Engine Documentation

## Overview

Multi-channel notification delivery with severity levels.

## Channels

- Email
- Slack
- Discord
- Telegram
- Webhook
- Custom

## Severity Levels

- Info
- Warning
- Error
- Critical

## Usage

```python
from notification.engine import NotificationEngine

engine = NotificationEngine(db, event_bus)
engine.register_provider("email", EmailProvider())

notification_id = engine.send_notification(
    channel="email",
    recipient="admin@maha.com",
    subject="Publication Complete",
    body="Product ML-123 published successfully",
    severity="info"
)
```

## Features

- Multi-channel support
- Severity levels
- Retry on failure
- Delivery tracking