# Memory Engine

## Overview

The Memory Engine manages different types of memory for the knowledge platform. It stores and retrieves operational knowledge, decisions, patterns, and customer insights.

## Memory Types

### Short-term Memory
- Temporary storage for recent events
- TTL-based expiration
- Used for current session context

### Long-term Memory
- Permanent storage for important knowledge
- Versioned and audited
- Used for historical learning

### Decision Memory
- Stores all optimization decisions
- Includes reasoning and outcomes
- Used for explainability

### Operational Memory
- Stores operational procedures
- Business rules
- System configurations

### Business Rules Memory
- Stores business policies
- Compliance rules
- Decision criteria

### Experiment Memory
- Stores experiment configurations
- Results and outcomes
- Success/failure patterns

### Customer Insights Memory
- Stores customer behavior patterns
- Preferences and segments
- Churn risk indicators

## Memory Flow

```
Store → Retrieve → Update → Expire → Delete
```

## Example Memory Item

```json
{
  "memory_id": "mem-1234567890-abc123",
  "memory_type": "decision",
  "key": "pricing_decision_opt-123",
  "value": {
    "decision": "approve",
    "reason": "High confidence and low risk",
    "confidence": 0.82,
    "risk_score": 0.25
  },
  "expires_at": null,
  "access_count": 5,
  "metadata": {
    "category": "pricing",
    "optimization_id": "opt-123"
  }
}
```

## Memory Statistics

```json
{
  "short_term": {
    "size": 150,
    "keys": ["event_1", "event_2", ...]
  },
  "long_term": {
    "size": 1200,
    "keys": ["knowledge_1", "knowledge_2", ...]
  },
  "decision": {
    "size": 45,
    "keys": ["dec_1", "dec_2", ...]
  }
}
```
