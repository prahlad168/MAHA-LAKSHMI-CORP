# MAHA SALES ENGINE V1 - Subscription Engine Documentation

## Overview

Subscription lifecycle management.

## Plans

- Monthly
- Quarterly
- Yearly
- Lifetime
- Trial

## Features

- Auto renewal
- Pause/Resume
- Cancel
- Upgrade/Downgrade
- Grace period
- Trial management

## Usage

```python
from subscriptions.engine import SubscriptionEngine

engine = SubscriptionEngine(db_manager, event_bus)

# Create subscription
subscription_id = engine.create_subscription(
    customer_id="cust-123",
    product_id="prod-123",
    plan_id="monthly"
)

# Cancel
engine.cancel_subscription(subscription_id)

# Pause
engine.pause_subscription(subscription_id)

# Resume
engine.resume_subscription(subscription_id)
```

## Events

- SubscriptionCreated
- SubscriptionRenewed
- SubscriptionCancelled
- SubscriptionPaused
- SubscriptionResumed