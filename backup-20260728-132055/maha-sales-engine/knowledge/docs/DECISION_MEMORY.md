# Decision Memory

## Overview

Decision Memory stores all optimization decisions with complete context, reasoning, and outcomes. It enables explainability, learning, and continuous improvement of the decision-making process.

## Decision Storage

Every decision is stored with:
- Decision ID
- Optimization ID
- Category
- Decision (approve/reject/execute)
- Reason
- Evidence
- Confidence Score
- Risk Score
- Outcome
- Reward
- Timestamp

## Decision Flow

```
Decision Made → Store Memory → Execute → Record Outcome → Update Reward → Learn
```

## Example Decision Memory

```json
{
  "memory_id": "dm-1234567890-abc123",
  "decision_id": "dec-1234567890-xyz789",
  "optimization_id": "opt-1234567890-xyz789",
  "category": "pricing",
  "decision": "approve",
  "reason": "High confidence (0.82) and low risk (0.25)",
  "evidence": {
    "current_price": 100,
    "recommended_price": 110,
    "competitor_analysis": "competitive"
  },
  "confidence": 0.82,
  "risk_score": 0.25,
  "outcome": {
    "revenue_increase": 0.15,
    "conversion_change": -0.02
  },
  "reward": 0.75,
  "created_at": "2024-01-01T10:00:00"
}
```

## Learning from Decisions

### Successful Decisions
- High reward → Reinforce pattern
- Update confidence models
- Share best practices

### Failed Decisions
- Low reward → Identify issues
- Update risk models
- Prevent similar mistakes

## Decision Analytics

```json
{
  "category": "pricing",
  "total_decisions": 150,
  "approved": 120,
  "rejected": 30,
  "avg_confidence": 0.78,
  "avg_risk": 0.32,
  "avg_reward": 0.65,
  "success_rate": 0.75
}
```
