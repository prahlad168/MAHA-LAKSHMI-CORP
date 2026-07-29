# Decision Engine

## Overview

The Decision Engine creates optimization decisions with complete reasoning, evidence, confidence scores, risk assessments, expected impact, and rollback plans.

## Decision Structure

Every decision includes:
- Decision ID
- Reason
- Evidence
- Confidence Score
- Risk Score
- Expected Impact
- Rollback Plan
- Related Metrics

## Decision Flow

```
Optimization Request → Simulation → Confidence/Risk Calculation → Decision Creation
    ↓
    ├── Low Confidence → Reject or Request More Data
    ├── High Risk → Request Approval
    └── Approved → Execute Optimization
```

## Confidence Thresholds

- **90%+**: High confidence, autonomous execution allowed
- **70-89%**: Medium confidence, approval required
- **60-69%**: Low confidence, recommendation only
- **<60%**: Insufficient confidence, reject

## Risk Thresholds

- **0.0-0.3**: Low risk, autonomous execution allowed
- **0.3-0.6**: Medium risk, approval required
- **0.6-0.8**: High risk, requires senior approval
- **>0.8**: Critical risk, reject

## Example Decision

```json
{
  "decision_id": "dec-1234567890-abc123",
  "optimization_id": "opt-1234567890-xyz789",
  "reason": "Conversion rate below 2% threshold, SEO optimization recommended",
  "evidence": {
    "current_conversion": 0.015,
    "historical_average": 0.025,
    "trend": "declining"
  },
  "confidence": 0.82,
  "risk_score": 0.25,
  "expected_impact": {
    "revenue": 1500.0,
    "conversion": 0.008,
    "traffic": 500.0
  },
  "rollback_plan": {
    "steps": ["Restore previous meta tags", "Verify rankings", "Monitor for 24h"],
    "estimated_time": "15 minutes"
  },
  "related_metrics": ["conversion_rate", "revenue", "organic_traffic"],
  "status": "approved",
  "decided_by": "admin"
}
```
