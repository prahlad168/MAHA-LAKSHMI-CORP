# MAHA SALES ENGINE V1 - Coupon Engine Documentation

## Overview

Coupon and discount management.

## Coupon Types

- Percentage
- Fixed Amount
- Bundle
- Referral
- Launch
- Seasonal
- Limited Time
- Customer Specific

## Usage

```python
from coupons.engine import CouponEngine

engine = CouponEngine(db_manager)

# Validate coupon
coupon = engine.validate_coupon(
    code="SUMMER2026",
    order_id="order-123"
)

# Apply discount
discount = engine.apply_coupon(coupon, order_total)
```

## Features

- Usage limits
- Customer restrictions
- Product restrictions
- Date range validation
- Minimum purchase
- Maximum discount cap