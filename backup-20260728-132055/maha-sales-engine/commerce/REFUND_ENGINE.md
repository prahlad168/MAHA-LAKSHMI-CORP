# MAHA SALES ENGINE V1 - Refund Engine Documentation

## Overview

Refund processing and management.

## Refund Flow

```
Refund Requested → Validate → Process → Notify → Complete
```

## Usage

```python
from refunds.engine import RefundEngine

engine = RefundEngine(db_manager, event_bus)

# Create refund
refund_id = engine.create_refund(
    order_id="order-123",
    amount=29.99,
    reason="Customer request"
)

# Process refund
engine.process_refund(refund_id)
```

## Features

- Partial refunds
- Full refunds
- Refund reasons
- Provider integration
- Audit trail
- Notification