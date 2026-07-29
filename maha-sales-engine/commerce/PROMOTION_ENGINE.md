# MAHA SALES ENGINE V1 - Promotion Engine Documentation

## Overview

Promotion campaign management.

## Promotion Types

- Launch
- Seasonal
- Flash Sale
- Holiday
- Bundle
- Cross Marketplace

## Usage

```python
from promotions.engine import PromotionEngine

engine = PromotionEngine(db_manager)

# Get active promotions
promotions = engine.get_active_promotions()

# Check eligibility
eligible = engine.check_eligibility(promotion_id, customer_id, order_data)
```

## Features

- Date-based activation
- Priority ordering
- Eligibility rules
- Marketplace linking
- Campaign linking