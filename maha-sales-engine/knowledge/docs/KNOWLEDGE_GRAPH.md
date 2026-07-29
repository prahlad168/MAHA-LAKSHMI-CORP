# Knowledge Graph

## Overview

The Knowledge Graph represents relationships among products, customers, campaigns, marketplaces, licenses, orders, recommendations, policies, experiments, and revenue. It enables querying and reasoning about complex business relationships.

## Node Types

- Product
- Customer
- Campaign
- Marketplace
- License
- Order
- Recommendation
- Policy
- Experiment
- Revenue

## Edge Types

- PURCHASED: Customer purchased product
- OPTIMIZED: Optimization was applied
- RECOMMENDED: Recommendation was made
- COMPLIED: Policy was complied with
- TESTED: Experiment was conducted
- GENERATED: Revenue was generated
- INFLUENCED: One entity influenced another
- RELATED: General relationship

## Example Graph

```
[Product A] --PURCHASED--> [Customer A]
[Product A] --OPTIMIZED--> [Optimization 1]
[Optimization 1] --RECOMMENDED--> [Recommendation 1]
[Recommendation 1] --COMPLIED--> [Policy 1]
[Customer A] --GENERATED--> [Revenue 1]
[Campaign 1] --INFLUENCED--> [Customer A]
```

## Graph Queries

### Find Customer Purchase History
```
Customer A → PURCHASED → Products
```

### Find Optimization Impact
```
Optimization 1 → RECOMMENDED → Recommendation 1 → COMPLIED → Policy 1
```

### Find Revenue Sources
```
Customer A → GENERATED → Revenue 1
Product A → PURCHASED → Customer A
```

## Graph Statistics

```json
{
  "total_nodes": 1500,
  "total_edges": 3200,
  "node_types": {
    "product": 500,
    "customer": 800,
    "campaign": 100,
    "marketplace": 50,
    "license": 30,
    "order": 400,
    "recommendation": 200,
    "policy": 50,
    "experiment": 100,
    "revenue": 270
  }
}
```
