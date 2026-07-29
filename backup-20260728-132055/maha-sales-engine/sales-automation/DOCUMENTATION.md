# MAHA SALES ENGINE V1 - Sales Automation Engine Documentation

## Overview

Complete operational lifecycle orchestration for digital product publication.

## Contents

### Core Documentation
- [SALES_AUTOMATION_ENGINE.md](SALES_AUTOMATION_ENGINE.md) - Main engine documentation
- [WORKFLOW_BUILDER.md](WORKFLOW_BUILDER.md) - Workflow builder guide
- [WORKFLOW_ENGINE.md](WORKFLOW_ENGINE.md) - Workflow engine guide
- [RULE_ENGINE.md](RULE_ENGINE.md) - Rules engine guide
- [POLICY_ENGINE.md](POLICY_ENGINE.md) - Policy engine guide
- [PUBLICATION_ENGINE.md](PUBLICATION_ENGINE.md) - Publication engine guide
- [QUEUE_ENGINE.md](QUEUE_ENGINE.md) - Queue architecture
- [RETRY_MANAGER.md](RETRY_MANAGER.md) - Retry strategies
- [WEBHOOK_GATEWAY.md](WEBHOOK_GATEWAY.md) - Webhook guide
- [NOTIFICATION_ENGINE.md](NOTIFICATION_ENGINE.md) - Notification guide
- [OBSERVABILITY.md](OBSERVABILITY.md) - Monitoring guide

## Quick Start

```python
from sales_automation.core.engine import AutomationCore
from pathlib import Path

core = AutomationCore(Path(__file__).parent.parent.parent)

# Publish product
result = core.publication_engine.publish_single("gumroad", "ML-20260727-000001", product_data)

# Create campaign
campaign_id = core.campaign_engine.create_campaign(
    name="Launch Campaign",
    campaign_type="launch",
    product_ids=["ML-20260727-000001"],
    marketplace_ids=["gumroad", "etsy"]
)
```

## API Documentation

Start the API server:
```bash
python -m sales_automation.api.routes
```

API docs available at: http://localhost:8004/api/docs

## Status

| Component | Status |
|-----------|--------|
| Automation Core | ✅ |
| Workflow Engine | ✅ |
| Queue Engine | ✅ |
| Retry Manager | ✅ |
| Publication Engine | ✅ |
| Sync Engine | ✅ |
| Approval Engine | ✅ |
| Rules Engine | ✅ |
| Policy Engine | ✅ |
| Notification Engine | ✅ |
| Webhook Gateway | ✅ |
| Health Monitor | ✅ |
| Audit Engine | ✅ |
| Metrics Collector | ✅ |
| Campaign Engine | ✅ |
| REST API | ✅ |
| Tests | ✅ |
| Documentation | ✅ |