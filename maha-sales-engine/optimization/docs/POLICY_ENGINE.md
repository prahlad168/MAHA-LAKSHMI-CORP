# Policy Engine

## Overview

The Policy Engine validates every optimization against business, risk, compliance, marketplace, and financial policies. No optimization may bypass the Policy Engine.

## Policy Types

### Business Policy
- Price change limits
- Category restrictions
- Performance thresholds
- Quality standards

### Risk Policy
- Maximum risk score thresholds
- High-risk approval requirements
- Risk mitigation requirements

### Compliance Policy
- Marketplace terms of service
- Legal requirements
- Data privacy rules
- Industry regulations

### Marketplace Policy
- Platform-specific rules
- Listing requirements
- Prohibited practices
- Category guidelines

### Financial Policy
- Budget limits
- Revenue impact thresholds
- Autonomous mode limits
- Approval thresholds

## Policy Evaluation

```
Optimization → Policy Engine → Evaluate All Policies
    ↓
    ├── All Passed → ALLOWED
    ├── Some Require Approval → REQUIRES_APPROVAL
    └── Any Failed → DENIED
```

## Default Policies

1. **Maximum Price Change**: Price changes cannot exceed 50%
2. **High Risk Approval**: Risk score above 0.8 requires approval
3. **Autonomous Mode Limit**: Autonomous mode only for optimizations under $1000 expected impact
4. **Marketplace Compliance**: Must comply with marketplace terms of service
5. **Minimum Confidence**: Confidence must be above 60%

## Example Policy Evaluation

```json
{
  "evaluation_id": "eval-1234567890-abc123",
  "optimization_id": "opt-1234567890-xyz789",
  "result": "allowed",
  "reason": "All policies passed",
  "details": {
    "policies_checked": 5,
    "violations": [],
    "requires_approval": false
  }
}
```

## Adding Custom Policies

```python
policy = Policy(
    policy_id="pol-006",
    name="Custom Policy",
    description="Custom policy description",
    policy_type=PolicyType.BUSINESS,
    rules=[
        {"field": "custom_field", "operator": "<=", "value": 100}
    ]
)
policy_engine.add_policy(policy)
```
