# Performance Review - MAHA SALES ENGINE V1

**Review Date:** 2026-07-27
**Reviewer:** Chief Software Architect (Phase 8.5)
**Scope:** Full platform performance characteristics

---

## 1. Executive Summary

The MAHA SALES ENGINE V1 platform has **no performance benchmarks, no load testing, and no profiling data**. Performance characteristics are inferred from code analysis and configuration values. The platform is designed for a single-node deployment with SQLite as the database, which imposes significant scalability limitations.

**Overall Performance Score: 38/100**

| Dimension | Score | Rating |
|-----------|-------|--------|
| Response Time | 30 | Poor |
| Throughput | 25 | Poor |
| Scalability | 35 | Poor |
| Resource Efficiency | 45 | Fair |
| Database Performance | 40 | Fair |
| Caching | 20 | Poor |
| Concurrency | 45 | Fair |

---

## 2. Response Time Analysis

### API Endpoints (No Measured Data)

The three FastAPI applications (`commerce/api/routes.py`, `marketing-engine/api/routes.py`, `sales-automation/api/routes.py`) have **no middleware for response time logging** and **no performance benchmarks**.

| Endpoint | Expected Latency | Evidence |
|----------|-----------------|----------|
| `/health` | < 10ms | Simple dict return |
| `/api/v1/customers` (GET) | < 50ms | SQLite query |
| `/api/v1/orders` (POST) | < 100ms | SQLite insert + JSON write |
| `/api/v1/generate` (POST) | Unknown | Queued job, no SLA |
| `/api/v1/metrics` | < 50ms | In-memory aggregation |

**Critical Finding:** No endpoint has a documented or measured response time target. The GLOBAL_EXECUTION_POLICY.md Section 14.2 targets `< 100ms` for API responses, but there is no mechanism to measure or enforce this.

### Core Engine Loop

The `CoreEngine.run()` method at `core/engine.py:468-480` uses `time.sleep(1)` in a busy-wait loop. This means the main thread wakes every 1 second to check the engine state, consuming unnecessary CPU cycles.

**Evidence:** `maha-sales-engine/core/engine.py:475` - `time.sleep(1)`

### Scheduler Loop

The `Scheduler._scheduler_loop()` at `scheduler/scheduler.py:109-117` checks jobs every 10 seconds. This is reasonable for a batch processing system but may be too slow for real-time operations.

**Evidence:** `maha-sales-engine/scheduler/scheduler.py:114` - `time.sleep(10)`

---

## 3. Throughput Analysis

### Scheduler Throughput

The scheduler has 4 worker threads (`scheduler.py:61` - `self.num_workers = 4`) and uses a `PriorityQueue`. Jobs are processed sequentially within each worker thread.

**Bottleneck:** The `_execute_job()` method at `scheduler/scheduler.py:160-188` runs jobs synchronously within the worker thread. If a job blocks (e.g., an HTTP call with a 30-second timeout), it blocks the entire worker thread.

**Evidence:** `maha-sales-engine/scheduler/scheduler.py:170` - `result = job.func(*job.args, **job.kwargs)` (synchronous execution)

### Database Throughput

SQLite is used as the database backend. SQLite supports:
- **1 writer at a time** (database-level locking)
- **Multiple readers concurrently**
- **No connection pooling** (each module creates its own connection)

**Critical Finding:** With 3 separate FastAPI apps each creating their own `DatabaseManager` instance, and the core engine also creating one, there are potentially **4+ concurrent connections** to the same SQLite file. SQLite's write lock will serialize all write operations, creating a bottleneck.

**Evidence:**
- `core/engine.py:177-182` - `DatabaseManager.get_connection()` creates a single connection
- `commerce/api/routes.py:43` - Creates its own `DatabaseManager`
- `marketing-engine/api/routes.py:41` - Creates its own `DatabaseManager`
- `sales-automation/api/routes.py:36` - Creates its own `DatabaseManager`

### Marketplace Throughput

The `MarketplaceManager` at `marketplaces/manager.py` has **no actual API integration**. All marketplace operations (create listing, publish, sync) are stub implementations that return placeholder data. Real throughput cannot be measured.

**Evidence:** `maha-sales-engine/marketplaces/manager.py:93` - "In production: call marketplace API to create listing"

---

## 4. Scalability Analysis

### Horizontal Scaling

The architecture is **not designed for horizontal scaling**:

1. **SQLite database** - File-based, not network-accessible. Cannot be shared across nodes.
2. **No message queue** - The `Scheduler` uses an in-memory `PriorityQueue` that is not shared across processes.
3. **No shared state** - Each module maintains its own in-memory state (e.g., `ProductManager.products`, `MarketplaceManager.listings`).
4. **No node discovery** - The `PerformanceReporter` sends heartbeats to a single dashboard URL with no load balancing.

**Evidence:** `maha-sales-engine/config/engine.yaml:46` - `"path": "./db/maha_sales_engine.db"` (local file path)

### Vertical Scaling

The platform can scale vertically by:
1. Increasing worker threads in the scheduler (currently hardcoded to 4)
2. Increasing the priority queue size (no limit configured)
3. Adding more memory for in-memory caches

**Limitation:** The `DatabaseManager` uses a single persistent connection with no connection pooling, limiting concurrent database access.

### Concurrency Model

| Component | Concurrency Model | Limitation |
|-----------|------------------|------------|
| Core Engine | Single thread (main loop) | Blocking on `time.sleep(1)` |
| Scheduler | 4 worker threads + 1 scheduler thread | GIL-limited for CPU-bound work |
| FastAPI apps | Async (uvicorn) | Each app runs on its own process |
| Database | Single SQLite connection per module | Write serialization |

---

## 5. Database Performance

### Schema Analysis

The main schema (`db/schema.sql`) has 10 tables with 13 indexes. The commerce schema (`commerce/db/schema.sql`) has 30+ tables with 16 indexes.

**Issues identified:**

1. **No composite indexes** - All indexes are single-column. Queries filtering on multiple columns (e.g., `status + created_at`) will require full table scans.
2. **TEXT fields for JSON data** - `features`, `metadata`, `purchase_history`, etc. are stored as TEXT with `json.dumps()`/`json.loads()`. This prevents database-level indexing and querying of nested fields.
3. **No partitioning** - All data is in a single table with no partitioning strategy.
4. **No vacuum/autocompact** - SQLite databases can fragment over time with frequent inserts/deletes.

**Evidence:**
- `db/schema.sql:192` - `features TEXT` (JSON stored as text)
- `db/schema.sql:258` - `metadata TEXT` (JSON stored as text)
- `commerce/db/schema.sql:11` - `billing_profile TEXT` (JSON stored as text)

### Query Patterns

The `Analytics.get_today_metrics()` method at `analytics/engine.py:49-91` executes 4 separate SQL queries per call. This is inefficient - a single query with JOINs would be faster.

**Evidence:** `maha-sales-engine/analytics/engine.py:56-76` - 4 separate cursor.execute() calls

### Connection Management

Each `DatabaseManager` instance creates a single `sqlite3.Connection` that is never pooled:

```python
# core/engine.py:177-182
def get_connection(self) -> sqlite3.Connection:
    if not self.connection:
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
    return self.connection
```

**Issue:** No connection timeout, no busy timeout, no WAL mode configuration. Under concurrent access, SQLite will raise `OperationalError: database is locked`.

---

## 6. Caching Analysis

### Existing Caching

| Cache | Location | Type | TTL |
|-------|----------|------|-----|
| ProductManager.products | In-memory dict | Write-through | None (stale after init) |
| MarketplaceManager.listings | In-memory dict | Write-through | None (stale after init) |
| ContentEngine.templates | In-memory dict | Static | None |
| MarketIntelligence.market_data | In-memory dict | Static | None |
| Scheduler.job_queue | In-memory PriorityQueue | Transient | None |

**Critical Finding:** There is **no caching layer** for frequently accessed data. Every API call that queries the database hits SQLite directly. There is no Redis, Memcached, or in-memory cache.

### Missing Caching Opportunities

1. **Product catalog** - Products are loaded once at startup and cached in memory, but never refreshed.
2. **Market analysis results** - `MarketIntelligence.analyze_digital_product_trends()` returns hardcoded data; no caching needed because it's already static.
3. **Dashboard summary** - `Analytics.get_dashboard_summary()` executes 8+ SQL queries per call; should be cached for at least 60 seconds.
4. **API response caching** - No HTTP caching headers are set on any FastAPI endpoint.

---

## 7. Resource Usage

### Memory

- **Core engine**: ~50 MB estimated (Python runtime + modules)
- **SQLite**: File-based, grows with data
- **FastAPI apps**: ~30 MB each (3 apps = ~90 MB additional)
- **Total estimated**: ~150 MB for a single-node deployment

**Evidence:** `GLOBAL_EXECUTION_POLICY.md:14.1` targets `< 100 MB` memory usage, but the current architecture with 3 separate FastAPI apps will exceed this.

### CPU

- **Core engine loop**: `time.sleep(1)` - minimal CPU
- **Scheduler**: 4 worker threads polling queue every 5 seconds
- **FastAPI apps**: Async, event-driven - efficient for I/O-bound work
- **Market intelligence**: All analysis methods return hardcoded data - zero CPU cost

### Disk

- **SQLite database**: Grows indefinitely with no retention policy for old data
- **Log files**: 5 files × 10 MB each (50 MB total) per the config
- **No disk usage monitoring** in the health check

---

## 8. Performance Targets vs. Reality

| Target (from GLOBAL_EXECUTION_POLICY.md) | Current Status | Gap |
|------------------------------------------|---------------|-----|
| API response time < 100ms | Not measured | No instrumentation |
| Database query performance | Not measured | No query logging |
| CPU < 5% | Not measured | No profiling |
| Memory < 100 MB | Likely exceeded with 3 FastAPI apps | Architecture issue |
| Uptime 99.9% | No monitoring | No health checks for API apps |
| Throughput: 50 leads/day | Not measured | No throughput testing |

---

## 9. Recommendations

1. **Add response time middleware** to all FastAPI apps to measure and log API latency
2. **Implement connection pooling** for SQLite (use `sqlite3.Connection` with `timeout` parameter)
3. **Enable WAL mode** for SQLite to improve concurrent read/write performance
4. **Add Redis or in-memory caching** for frequently accessed data (product catalog, dashboard summary)
5. **Consolidate the 3 FastAPI apps** into a single application to reduce memory footprint
6. **Add composite indexes** to database schema for common query patterns
7. **Implement database vacuum** scheduling to prevent fragmentation
8. **Add query result caching** with TTL for dashboard and analytics endpoints
9. **Add load testing** with a tool like `locust` or `k6` to establish baseline performance
10. **Add profiling** with `cProfile` or `py-spy` to identify bottlenecks

---

*End of Performance Review*