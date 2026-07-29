# MAHA SALES ENGINE V1 - Digital Delivery Documentation

## Overview

Secure digital product delivery with download management.

## Features

- Secure download URLs
- Expiring links
- One-time download support
- Download limits
- Watermark metadata
- Delivery retry
- Delivery confirmation
- Integrity verification (checksums)

## Usage

```python
from delivery.engine import DigitalDeliveryEngine

engine = DigitalDeliveryEngine(db_manager, output_dir)

# Create delivery
delivery_id = engine.create_delivery(
    order_id="order-123",
    product_id="prod-123",
    file_path="/path/to/product.zip",
    expires_in_hours=24
)

# Get download URL
url = engine.get_download_url(delivery_id)

# Record download
engine.record_download(delivery_id, "127.0.0.1", "Mozilla/5.0")
```

## Security

- HMAC-signed tokens
- Time-based expiration
- IP tracking
- User agent logging
- Download count limits
- Integrity checksums