# MAHA SALES ENGINE V1 - License Engine Documentation

## Overview

License generation, activation, and management.

## License Types

- Personal
- Commercial
- Extended
- Enterprise
- Subscription
- Lifetime
- Trial
- Custom

## License Flow

```
Order Paid → Issue License → Activate → Validate → Use → Renew/Revoke
```

## Usage

```python
from licenses.engine import LicenseEngine

engine = LicenseEngine(db_manager)

# Issue license
license_id = engine.issue_license(
    customer_id="cust-123",
    product_id="prod-123",
    order_id="order-123",
    license_type="commercial",
    metadata={"max_activations": 3}
)

# Activate license
engine.activate_license(license_id, {"ip": "127.0.0.1", "device": "MacBook Pro"})

# Validate license
license_data = engine.validate_license("LICENSE-KEY-123")
```

## Features

- Secure key generation
- Activation tracking
- Expiration management
- Revocation support
- Transfer support
- Validation API