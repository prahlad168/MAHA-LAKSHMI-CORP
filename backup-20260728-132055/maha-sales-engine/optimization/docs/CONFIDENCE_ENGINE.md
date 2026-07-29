# Confidence Engine

## Overview

The Confidence Engine calculates confidence scores for optimization recommendations. Recommendations below configurable thresholds must never execute automatically.

## Confidence Factors

### Historical Accuracy (30%)
- Past optimization success rate
- Category-specific accuracy
- Time-weighted performance

### Data Quality (20%)
- Data completeness
- Missing data percentage
- Data freshness

### Sample Size (20%)
- Number of data points
- Statistical significance
- Confidence in measurements

### Simulation Consistency (20%)
- Simulation variance
- Model stability
- Prediction reliability

### Market Stability (10%)
- Market volatility
- Competitive landscape
- External factors

## Confidence Calculation

```
Confidence = Σ(Factor Score × Weight)
```

## Thresholds

- **90%+**: High confidence - autonomous execution allowed
- **70-89%**: Medium confidence - approval required
- **60-69%**: Low confidence - recommendation only
- **<60%**: Insufficient confidence - reject

## Example Confidence Score

```json
{
  "score": 0.82,
  "factors": {
    "historical_accuracy": 0.85,
    "data_quality": 0.90,
    "sample_size": 0.75,
    "simulation_consistency": 0.80,
    "market_stability": 0.85
  },
  "explanation": "High confidence based on strong historical performance and quality data"
}
```

## Configuration

```python
confidence_engine = ConfidenceEngine(config={
    "min_confidence": 0.6,
    "weights": {
        "historical_accuracy": 0.3,
        "data_quality": 0.2,
        "sample_size": 0.2,
        "simulation_consistency": 0.2,
        "market_stability": 0.1
    }
})
```
