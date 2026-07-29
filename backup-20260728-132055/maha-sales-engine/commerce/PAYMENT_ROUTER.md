# MAHA SALES ENGINE V1 - Payment Router Documentation

## Overview

Automatically select payment provider based on configurable rules.

## Routing Rules

- Priority
- Fallback
- Geographic Rules
- Currency Rules
- Product Rules

## Usage

```python
from payments.router import PaymentRouter

router = PaymentRouter(db_manager, provider_registry)

router.add_rule({
    "name": "Stripe for USD",
    "priority": 1,
    "conditions": {
        "currency": {"operator": "eq", "value": "USD"},
        "country": {"operator": "in", "value": ["US", "CA"]}
    },
    "provider": "stripe"
})

router.add_rule({
    "name": "PayPal fallback",
    "priority": 2,
    "conditions": {
        "currency": {"operator": "eq", "value": "USD"}
    },
    "provider": "paypal"
})

provider = router.route({
    "currency": "USD",
    "country": "US",
    "amount": 29.99
})
```

## Features

- Rule-based routing
- Automatic fallback
- Geographic routing
- Currency routing
- Load balancing