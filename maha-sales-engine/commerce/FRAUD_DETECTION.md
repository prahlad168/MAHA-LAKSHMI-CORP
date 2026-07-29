# MAHA SALES ENGINE V1 - Fraud Detection Documentation

## Overview

Fraud detection and prevention.

## Detection Methods

- Duplicate Orders
- Velocity Checks
- Suspicious IP
- Country Restrictions
- Repeated Failures
- Blacklist
- Risk Score

## Usage

```python
from fraud.engine import FraudDetectionEngine

engine = FraudDetectionEngine(db_manager)

# Check order
risk_score = engine.check_order(order_id, customer_id, payment_data)

# Get fraud events
events = engine.get_fraud_events(order_id)
```

## Risk Scoring

- 0-30: Low risk
- 31-60: Medium risk
- 61-80: High risk
- 81-100: Block

## Actions

- Allow
- Review
- Block
- Notify