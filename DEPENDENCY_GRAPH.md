# Dependency Graph - MAHA SALES ENGINE V1

**Generated:** 2026-07-27
**Scope:** Full platform architecture
**Purpose:** Visualize module dependencies, identify circular dependencies, hidden dependencies, and coupling issues

---

## 1. Core Engine Dependency Graph

```
main.py
│
├── core/engine.py
│   ├── logging
│   ├── threading
│   ├── sqlite3
│   ├── yaml
│   ├── psutil
│   └── pathlib
│
├── scheduler/scheduler.py
│   ├── queue (stdlib)
│   ├── threading
│   └── datetime
│
├── products/product-manager.py
│   ├── json
│   └── datetime
│
├── market-intelligence/analyzer.py
│   ├── json
│   └── random
│
├── marketplaces/manager.py
│   ├── json
│   └── datetime
│
├── content/engine.py
│   ├── json
│   ├── random          ⚠️ Imported at BOTTOM of file (line 205)
│   └── datetime
│
├── analytics/engine.py
│   ├── json
│   └── collections.defaultdict
│
├── reporter/reporter.py
│   ├── json
│   ├── requests        ⚠️ Imported but HTTPS calls are commented out
│   ├── hmac
│   ├── hashlib
│   └── datetime
│
└── config/engine.yaml  (loaded at runtime)
```

---

## 2. Commerce Module Dependency Graph

```
commerce/api/routes.py (FastAPI, port 8005)
│
├── core/engine.py (ConfigManager, DatabaseManager)
│   └── ⚠️ sys.path.insert(0, ...) at line 16
│
├── commerce/core/engine.py (CommerceCore)
│   ├── commerce/customers/engine.py
│   ├── commerce/orders/engine.py
│   ├── commerce/cart/engine.py
│   ├── commerce/checkout/engine.py
│   ├── commerce/payments/sdk.py
│   ├── commerce/payments/router.py
│   ├── commerce/licenses/engine.py
│   ├── commerce/subscriptions/engine.py
│   ├── commerce/delivery/engine.py
│   ├── commerce/invoices/engine.py
│   ├── commerce/receipts/engine.py
│   ├── commerce/coupons/engine.py
│   ├── commerce/promotions/engine.py
│   ├── commerce/tax/engine.py
│   ├── commerce/refunds/engine.py
│   ├── commerce/wallets/engine.py
│   ├── commerce/payouts/engine.py
│   ├── commerce/fraud/engine.py
│   ├── commerce/events/bus.py
│   ├── commerce/queue/engine.py
│   ├── commerce/audit/engine.py
│   ├── commerce/metrics/engine.py
│   └── commerce/health/monitor.py
│
└── commerce/db/schema.sql (417 lines, 20+ tables)
```

**⚠️ CRITICAL:** `commerce/api/routes.py` imports modules like:
- `payments.providers` (does not exist - should be `payments/sdk.py`)
- `orders.engine` (exists but imported via sys.path hack)
- `licenses.engine` (exists)
- `subscriptions.engine` (exists)
- `delivery.engine` (exists)
- `invoices.engine` (exists)
- `coupons.engine` (exists)
- `promotions.engine` (exists)
- `refunds.engine` (exists)
- `wallets.engine` (exists)
- `payouts.engine` (exists)
- `fraud.engine` (exists)
- `health.monitor` (exists)
- `metrics.engine` (exists)
- `audit.engine` (exists)

Many of these imports will fail at runtime because the module paths don't match the file structure.

---

## 3. Marketing Engine Dependency Graph

```
marketing-engine/api/routes.py (FastAPI, port 8003)
│
├── core/engine.py (ConfigManager, DatabaseManager)
│   └── ⚠️ sys.path.insert(0, ...) at line 16
│
├── marketing-engine/core/engine.py (MarketingEngine)
│   ├── ai/provider.py (AIProviderManager, AIConfig, AIMessage, BaseAIProvider)
│   ├── prompts/library.py (PromptLibrary, PromptTemplateFactory)
│   ├── pipeline/state_machine.py (ContentPipeline, ContentStatus, ContentPipelineStateMachine)
│   ├── seo/engine.py (SEOEngine)
│   ├── keywords/engine.py (KeywordEngine)
│   ├── quality/engine.py (ContentQualityEngine)
│   ├── brand/engine.py (BrandEngine)
│   ├── localization/engine.py (LocalizationEngine)
│   ├── ab_testing/engine.py (ABTestingEngine)
│   └── assets/engine.py (AssetGenerationEngine)
│
├── marketing-engine/events/bus.py (EventBus, MarketplaceEvents)
│
├── marketing-engine/queue/manager.py (MarketingJobQueue, JobPriority)
│
└── marketing-engine/db/schema.sql
```

---

## 4. Sales Automation Dependency Graph

```
sales-automation/api/routes.py (FastAPI, port 8004)
│
├── core/engine.py (ConfigManager, DatabaseManager)
│   └── ⚠️ sys.path.insert(0, ...) at line 16
│
├── sales-automation/core/engine.py (AutomationCore)
│   ├── events/bus.py (EventBus)
│   ├── workflow/engine.py (WorkflowEngine)
│   ├── queue/engine.py (QueueEngine)
│   ├── retry/manager.py (RetryManager)
│   ├── publication/engine.py (PublicationEngine)
│   ├── sync/engine.py (SynchronizationEngine)
│   ├── approval/engine.py (ApprovalEngine)
│   ├── rules/engine.py (RulesEngine)
│   ├── policy/engine.py (PolicyEngine)
│   ├── notification/engine.py (NotificationEngine, EmailProvider, SlackProvider)
│   ├── webhooks/gateway.py (WebhookGateway)
│   ├── health/monitor.py (HealthMonitor)
│   ├── audit/engine.py (AuditEngine)
│   ├── metrics/collector.py (MetricsCollector)
│   └── campaign/engine.py (CampaignEngine)
│
└── sales-automation/db/schema.sql
```

---

## 5. Parallel System Dependencies

### app/ Directory

```
app/main.py (FastAPI, port 8000)
│
├── app/core/gaurangga_bridge.py (GauranggaCommandBridge)
│   ├── enterprise-hub/ (offline-ledger.json, wire-tracking.json, procurement.json)
│   ├── ceo-revenue-share/ (01-config.json, 02-revenue-tracker.json, 03-audit-log.json)
│   └── sys.path hack at line 18
│
├── app/api/sales.py (APIRouter)
│   ├── sales-system/products.json
│   ├── sales-system/orders.json
│   └── sales-system/customers.json
│
└── ⚠️ NO integration with maha-sales-engine core
```

### autonomous-sales-agent/ Directory

```
autonomous-sales-agent/orchestrator.py
│
├── autonomous-sales-agent/core/sales-agent-core.py (AutonomousSalesAgent)
│   ├── autonomous-sales-agent/core/database.py (RealTimeDatabase)
│   ├── autonomous-sales-agent/core/market-analysis.py (MarketAnalyzer)
│   ├── autonomous-sales-agent/finance/finance-agent.py (AutonomousFinanceAgent)
│   └── autonomous-sales-agent/reporting/ceo-reporter.py (CEOReporter)
│
├── autonomous-sales-agent/webhooks/server.py
│
├── autonomous-sales-agent/workflows/__init__.py
│
├── autonomous-sales-agent/channels/__init__.py
│
└── ⚠️ Uses importlib.util for dynamic module loading
⚠️ NO integration with maha-sales-engine core
```

---

## 6. Circular Dependency Analysis

### Detected Circular Dependencies

| Cycle | Severity | Description |
|-------|----------|-------------|
| None in core engine | ✅ Clean | All dependencies flow downward |
| `sys.path.insert` chain | ⚠️ Medium | `commerce/core/engine.py`, `marketing-engine/core/engine.py`, `sales-automation/core/engine.py` all insert parent path, then import from `core.engine`. If `core.engine` is not importable (e.g., not on path), these will fail. |

### Hidden Dependencies

| Dependency | Location | Issue |
|------------|----------|-------|
| `core.engine` imported by 3 separate API route files | `commerce/api/routes.py:16`, `marketing-engine/api/routes.py:17`, `sales-automation/api/routes.py:17` | Each creates its own ConfigManager and DatabaseManager instance |
| `random` imported at bottom of `content/engine.py` | `content/engine.py:205` | Used at line 74 but imported at line 205 |
| `psutil` imported in `core/engine.py` | `core/engine.py:18` | Required at runtime but not listed in `requirements.txt` |
| `fastapi` imported in 3 API route files | Multiple | Not listed in `requirements.txt` |
| `uvicorn` imported in 3 API route files | Multiple | Listed as dev dependency only |
| `pydantic` imported in 3 API route files | Multiple | Not listed in `requirements.txt` |

---

## 7. Dependency Version Pinning

### requirements.txt Analysis

```
pyyaml>=6.0          ⚠️ Loose pin (>= instead of ==)
psutil>=5.9          ⚠️ Loose pin
requests>=2.31       ⚠️ Loose pin
schedule>=1.2        ⚠️ Loose pin
sqlalchemy>=2.0      ⚠️ Loose pin
python-dotenv>=1.0   ⚠️ Loose pin
cryptography>=41.0   ⚠️ Loose pin
pyjwt>=2.8           ⚠️ Loose pin
fastapi              ❌ NOT LISTED (used in commerce/api/routes.py)
pydantic             ❌ NOT LISTED (used in commerce/api/routes.py)
uvicorn              ❌ NOT LISTED (used in commerce/api/routes.py)
```

**Critical Finding:** `fastapi`, `pydantic`, and `uvicorn` are imported in the API route files but are **not listed in `requirements.txt`**. This will cause `pip install -r requirements.txt` to miss critical dependencies.

---

## 8. External Dependency Risk Matrix

| Dependency | Risk Level | Reason |
|------------|-----------|--------|
| `psutil` | Medium | Used in core engine but not in requirements.txt |
| `fastapi` | Critical | Used in 3 API files but not in requirements.txt |
| `pydantic` | Critical | Used in 3 API files but not in requirements.txt |
| `uvicorn` | Critical | Used in 3 API files but not in requirements.txt |
| `requests` | Medium | Imported in reporter but HTTPS calls are commented out |
| `pyyaml` | Low | Only used for config loading |
| `sqlite3` | Low | Stdlib, always available |
| `openai` | Low | Optional, listed as optional dependency |
| `anthropic` | Low | Optional, listed as optional dependency |
| `pywin32` | Low | Windows-only, platform-filtered |

---

## 9. Dependency Graph Summary

### Module Interconnection Map

```
                    ┌─────────────────────┐
                    │   main.py (entry)   │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   core/engine.py    │
                    │  (Config, DB, Health)│
                    └──────────┬──────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
   │  Scheduler   │  │  Product Mgr │  │  Market Intel│
   └──────────────┘  └──────────────┘  └──────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
   │  Marketplace │  │   Content    │  │  Analytics   │
   │  Manager     │  │   Engine     │  │  Engine      │
   └──────────────┘  └──────────────┘  └──────────────┘
          │                    │                    │
          └────────────────────┼────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Performance       │
                    │  Reporter          │
                    └─────────────────────┘

    PARALLEL SYSTEMS (NOT INTEGRATED):
    
    ┌─────────────────┐    ┌─────────────────────┐
    │ app/ (FastAPI)  │    │ autonomous-sales-   │
    │ port 8000       │    │ agent/ (orchestrator)│
    │ GauranggaBridge │    │ port: N/A           │
    └─────────────────┘    └─────────────────────┘

    SEPARATE API APIS (no gateway):
    
    ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
    │ commerce/api    │  │ marketing-engine│  │ sales-automation│
    │ port 8005       │  │ port 8003       │  │ port 8004       │
    └─────────────────┘  └─────────────────┘  └─────────────────┘
```

---

## 10. Recommendations

1. **Add missing dependencies** to `requirements.txt`: `fastapi`, `pydantic`, `uvicorn`
2. **Pin all dependencies** with `==` instead of `>=` for reproducible builds
3. **Consolidate the 3 FastAPI apps** into a single application with blueprints
4. **Remove `sys.path.insert` hacks** - use proper package structure with `__init__.py` files
5. **Fix the `import random` placement** in `content/engine.py`
6. **Add a dependency injection container** instead of passing concrete types
7. **Create a unified database connection pool** shared across all modules

---

*End of Dependency Graph*