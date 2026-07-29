# MAHA SALES ENGINE V1 - Queue Engine Documentation

## Overview

Job queue with priority, scheduling, dead letter, and worker pools.

## Queue Types

- Priority Queue
- FIFO Queue
- Scheduled Queue
- Recurring Queue
- Retry Queue
- Dead Letter Queue

## Job Lifecycle

```
PENDING → QUEUED → RUNNING → COMPLETED
                            ↓
                          FAILED → RETRYING → RUNNING
                                                ↓
                                              FAILED → DEAD_LETTER
```

## Usage

```python
from queue.engine import QueueEngine, JobPriority

engine = QueueEngine(db_manager, max_workers=5)
engine.start()

job_id = engine.enqueue(
    "publish",
    {"marketplace_id": "gumroad", "product_id": "ML-123"},
    priority=JobPriority.HIGH
)

engine.register_handler("publish", handle_publish)
```

## Worker Pools

- Configurable worker count
- Load balancing
- Graceful shutdown
- Health monitoring

## Dead Letter Queue

- Automatic for permanent failures
- Manual retry support
- Error tracking