# MAHA SALES ENGINE V1 - Customer Engine Documentation

## Overview

Customer and organization management with billing profiles.

## Customer Types

- Individual Customer
- Organization

## Customer Data

- Contact Information
- Language Preference
- Currency Preference
- Billing Profile
- Purchase History
- Subscription History
- License History
- Download History

## Usage

```python
from customers.engine import CustomerEngine

engine = CustomerEngine(db_manager)

# Create customer
customer_id = engine.create_customer(
    email="customer@example.com",
    name="John Doe",
    language="en",
    currency="USD"
)

# Get customer
customer = engine.get_customer(customer_id)
```

## Organization Support

- Team members
- Centralized billing
- Admin/User roles
- Shared licenses