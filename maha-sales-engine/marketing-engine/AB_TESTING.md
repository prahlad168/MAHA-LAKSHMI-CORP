# MAHA SALES ENGINE V1 - A/B Testing Documentation

## Overview

A/B testing support for marketing content variants.

## Test Structure

- Test ID
- Product ID
- Content Type
- Variants (A, B, C)
- Metrics
- Winner

## Usage

```python
from ab_testing.engine import ABTestingEngine

engine = ABTestingEngine(db_manager)

# Create test
test_id = engine.create_test(
    product_id="prod-123",
    content_type="email",
    variants=[
        {"subject": "Subject A", "body": "Body A"},
        {"subject": "Subject B", "body": "Body B"}
    ]
)

# Get test
test = engine.get_test(test_id)
```

## Variants

- Variant A (Control)
- Variant B (Treatment)
- Variant C (Optional)

## Metrics

Track:
- Conversion rate
- Click-through rate
- Open rate
- Engagement time
- Bounce rate

## Best Practices

1. Test one variable at a time
2. Run tests for sufficient duration
3. Use statistical significance
4. Document learnings
5. Apply winners