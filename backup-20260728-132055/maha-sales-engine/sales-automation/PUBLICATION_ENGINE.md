# MAHA SALES ENGINE V1 - Publication Engine Documentation

## Overview

Single and bulk publication operations with approval and rules integration.

## Operations

- Single Publish
- Bulk Publish
- Bulk Update
- Bulk Archive
- Bulk Retry
- Bulk Synchronization
- Bulk Verification

## Usage

```python
from publication.engine import PublicationEngine

engine = PublicationEngine(db, registry, creds, event_bus, workflow, approval, rules)

# Single publish
result = engine.publish_single("gumroad", "ML-123", product_data)

# Bulk publish
result = engine.publish_bulk("gumroad", ["ML-123", "ML-456"], {})
```

## Integration

- Rules Engine validation
- Approval Engine integration
- Workflow Engine orchestration
- Event Bus notifications