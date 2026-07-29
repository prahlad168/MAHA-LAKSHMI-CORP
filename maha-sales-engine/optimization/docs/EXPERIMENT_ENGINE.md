# Experiment Engine

## Overview

The Experiment Engine supports safe optimization testing through A/B testing, canary rollout, shadow mode, gradual rollout, and automatic rollback.

## Experiment Types

### A/B Testing
- Split traffic between variants
- Statistical significance testing
- Automatic winner selection

### Canary Rollout
- Gradual traffic increase
- Real-time monitoring
- Automatic rollback on issues

### Shadow Mode
- Run optimization in parallel
- Compare without user impact
- Validate before full rollout

### Gradual Rollout
- Incremental traffic increase
- Stage-based deployment
- Performance monitoring at each stage

## Experiment Flow

```
Create Experiment → Start Experiment → Monitor Metrics → Analyze Results
    ↓
    ├── Success → Complete Experiment
    ├── Failure → Rollback Experiment
    └── Inconclusive → Extend Experiment
```

## Example Experiment

```json
{
  "experiment_id": "exp-1234567890-abc123",
  "optimization_id": "opt-1234567890-xyz789",
  "experiment_type": "canary",
  "status": "running",
  "config": {
    "initial_percentage": 10,
    "max_percentage": 100,
    "increment_step": 10,
    "step_duration_minutes": 60,
    "success_criteria": {
      "revenue_increase_min": 0.05,
      "error_rate_max": 0.01
    }
  }
}
```

## Automatic Rollback

Experiments automatically rollback when:
- Error rate exceeds threshold
- Revenue decreases significantly
- Performance degrades
- Policy violation detected
