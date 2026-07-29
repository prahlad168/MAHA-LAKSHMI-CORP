# Semantic Search

## Overview

The Semantic Search engine enables natural-language search across documentation, policies, past decisions, experiments, recommendations, and operational events. It uses vector embeddings to find semantically similar content.

## Search Process

```
Query → Embed Query → Search Index → Rank Results → Return Top K
```

## Search Features

### Natural Language Queries
- "How do we handle pricing?"
- "What were the results of the last SEO optimization?"
- "Show me decisions about customer retention"

### Multi-Source Search
- Documentation
- Policies
- Past decisions
- Experiments
- Recommendations
- Operational events

### Ranking
- Cosine similarity scoring
- Confidence weighting
- Recency boosting
- Source authority

## Example Search

### Query
```
"pricing optimization strategies"
```

### Results
```json
{
  "query": "pricing optimization strategies",
  "results": [
    {
      "result_id": "result-1234567890-abc123",
      "knowledge_id": "know-123",
      "score": 0.92,
      "snippet": "Document know-123",
      "metadata": {
        "knowledge_id": "know-123",
        "title": "Pricing Optimization Best Practices",
        "source": "optimization"
      }
    },
    {
      "result_id": "result-1234567890-def456",
      "knowledge_id": "know-456",
      "score": 0.85,
      "snippet": "Document know-456",
      "metadata": {
        "knowledge_id": "know-456",
        "title": "Competitor Price Analysis",
        "source": "marketplace"
      }
    }
  ]
}
```

## Embedding Service

The embedding service converts text to vector representations:
- Dimension: 128
- Normalized vectors
- Batch processing support

## Indexing

Documents are indexed automatically when:
- New knowledge is created
- Knowledge is updated
- Documents are imported
