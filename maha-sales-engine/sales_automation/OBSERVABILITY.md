# MAHA SALES ENGINE V1 - Observability Documentation

## Overview

Health monitoring, audit trail, and metrics collection.

## Health Monitoring

- Component health checks
- Uptime tracking
- Error monitoring
- Status aggregation

## Audit Trail

- Immutable records
- Action tracking
- Resource tracking
- Before/after snapshots

## Metrics

### Counters
- Total publications
- Success rate
- Retry count
- Queue length

### Timers
- Workflow duration
- Publish time
- Sync time
- Queue wait time

### Gauges
- Active workers
- Queue depth
- Circuit breaker state

## Usage

```python
from health.monitor import HealthMonitor
from audit.engine import AuditEngine
from metrics.collector import MetricsCollector

# Health
health = monitor.get_overall_health()

# Audit
audit_engine.log("publish", "admin", "marketplace", "mkt-123", before=old, after=new)

# Metrics
metrics_collector.increment("publications")
metrics_collector.timing("publish_time", 1500)
```

## Alerts

- Component unhealthy
- High error rate
- Queue backlog
- Circuit breaker open