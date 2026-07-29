# MAHA SALES ENGINE V1 - Order Engine Documentation

## Overview

Order management with comprehensive state machine.

## Order States

- Draft
- Pending Payment
- Authorized
- Paid
- Delivering
- Delivered
- Completed
- Cancelled
- Expired
- Refund Requested
- Refunded
- Failed

## State Machine

```
Draft → Pending Payment → Authorized → Paid → Delivering → Delivered → Completed
                    ↓              ↓         ↓
                  Failed ←←←←←←←←←←←←←←←←←←
                    ↓
              Refund Requested → Refunded
```

## Usage

```python
from orders.engine import OrderEngine

engine = OrderEngine(db_manager, event_bus)

# Create order
order_id = engine.create_order(
    customer_id="cust-123",
    items=[{"product_id": "prod-123", "quantity": 1}],
    total_amount=29.99,
    currency="USD"
)

# Update status
engine.update_status(order_id, "pending_payment")
engine.update_status(order_id, "paid")
```

## Features

- Atomic state transitions
- Rollback support
- Event emission
- Audit logging