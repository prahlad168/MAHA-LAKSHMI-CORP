# MAHA SALES ENGINE V1 - Retry Manager Documentation

## Overview

Retry policies and circuit breaker implementation.

## Retry Policies

- Immediate
- Linear
- Exponential Backoff
- Adaptive Retry

## Circuit Breaker States

- Closed - Normal operation
- Open - Failing, reject calls
- Half-Open - Testing recovery

## Usage

```python
from retry.manager import RetryManager, RetryPolicy

manager = RetryManager(db_manager)
manager.register_policy(
    "publish",
    policy=RetryPolicy.EXPONENTIAL_BACKOFF,
    max_retries=3,
    initial_delay=1.0,
    backoff_factor=2.0
)

if manager.should_retry("publish", retry_count):
    delay = manager.get_delay("publish", retry_count)
    time.sleep(delay)
```

## Circuit Breaker

- Automatic opening after threshold
- Automatic recovery after timeout
- Configurable thresholds