# MAHA SALES ENGINE V1 - Job Queue Documentation

## Overview

The Job Queue provides asynchronous processing for marketplace operations with retry support.

## Architecture

```
Producer → Priority Queue → Workers → Handlers
                ↓
           Retry Manager
                ↓
           Dead Letter Queue (future)
```

## Job Lifecycle

```
PENDING → RUNNING → COMPLETED
                ↓
              FAILED → RETRY → RUNNING
                            ↓
                          FAILED (permanent)
```

## Usage

```python
from queue.manager import JobQueue, JobPriority, RetryManager

queue = JobQueue(max_workers=5)
queue.start()

# Enqueue job
job_id = queue.enqueue(
    "publish",
    {"marketplace_id": "mkt-123", "product_id": "prod-456"},
    priority=JobPriority.HIGH,
    max_retries=3
)

# Register handler
def handle_publish(payload):
    # Do work
    return {"success": True}

queue.register_handler("publish", handle_publish)

# Check job status
job = queue.get_job(job_id)
print(job["state"])

# Cancel job
queue.cancel_job(job_id)

# Get stats
stats = queue.get_stats()
print(stats)
```

## Priorities

- `LOW` (0) - Background tasks
- `NORMAL` (1) - Standard operations
- `HIGH` (2) - User-initiated actions
- `CRITICAL` (3) - System-critical operations

## Retry Policy

```python
retry_manager = RetryManager()
retry_manager.register_policy(
    operation="publish",
    max_retries=3,
    backoff_factor=2.0,
    initial_delay=1.0
)

delay = retry_manager.get_delay("publish", retry_count=1)
# delay = 2.0 seconds (exponential backoff)
```

## States

- `pending` - Waiting to run
- `running` - Currently executing
- `waiting` - Waiting for dependency
- `retry` - Scheduled for retry
- `completed` - Successfully finished
- `cancelled` - Cancelled by user
- `failed` - Permanent failure

## Best Practices

1. Use appropriate priorities
2. Set reasonable timeouts
3. Implement idempotent handlers
4. Handle exceptions gracefully
5. Monitor queue depth
6. Log job lifecycle events