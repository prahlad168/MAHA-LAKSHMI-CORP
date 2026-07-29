# Database Review - MAHA SALES ENGINE V1

**Review Date:** 2026-07-27
**Reviewer:** Chief Software Architect (Phase 8.5)
**Scope:** All database schemas and data access patterns

---

## 1. Executive Summary

The MAHA SALES ENGINE V1 uses **SQLite** as its sole database backend. The platform has **two separate schema files** that define overlapping tables. The database design follows normalization principles partially but has significant issues with data type choices, missing indexes, and lack of migration support.

**Overall Database Score: 45/100**

| Dimension | Score | Rating |
|-----------|-------|--------|
| Schema Design | 50 | Fair |
| Normalization | 45 | Fair |
| Indexing | 50 | Fair |
| Data Integrity | 35 | Poor |
| Migration Support | 10 | Critical |
| Connection Management | 30 | Poor |
| Backup Strategy | 20 | Poor |
| Security | 25 | Poor |

---

## 2. Database Schema Analysis

### 2.1 Main Schema (`maha-sales-engine/db/schema.sql`)

**10 tables, 13 indexes**

| Table | Purpose | Rows (estimated) |
|-------|---------|-----------------|
| `products` | Digital product catalog | ~5 |
| `leads` | Lead management | Variable |
| `outreach_log` | Outreach tracking | Variable |
| `transactions` | Payment transactions | Variable |
| `reports` | Generated reports | Variable |
| `system_metrics` | System health metrics | Variable |
| `marketplace_listings` | Marketplace product listings | Variable |
| `content_templates` | Content templates | ~4 |

### 2.2 Commerce Schema (`maha-sales-engine/commerce/db/schema.sql`)

**30+ tables, 16 indexes**

| Table | Purpose |
|-------|---------|
| `customers` | Customer management |
| `organizations` | Organization/company accounts |
| `orders` | Order management |
| `order_items` | Order line items |
| `shopping_carts` | Shopping cart data |
| `payment_methods` | Saved payment methods |
| `payment_transactions` | Payment transaction records |
| `payment_providers` | Payment provider configuration |
| `payment_attempts` | Payment attempt history |
| `licenses` | License management |
| `license_activations` | License activation tracking |
| `subscriptions` | Subscription management |
| `subscription_events` | Subscription event log |
| `deliveries` | Digital product delivery |
| `download_logs` | Download tracking |
| `invoices` | Invoice generation |
| `receipts` | Receipt generation |
| `coupons` | Coupon management |
| `promotions` | Promotion management |
| `promotion_rules` | Promotion rule definitions |
| `refunds` | Refund processing |
| `wallets` | Customer wallet balances |
| `wallet_transactions` | Wallet transaction history |
| `payouts` | Payout distribution |
| `tax_rules` | Tax calculation rules |
| `fraud_events` | Fraud detection events |
| `commerce_events` | Commerce event log |
| `commerce_audit_log` | Audit trail |
| `commerce_metrics` | Commerce metrics |
| `commerce_health` | Commerce component health |

### 2.3 Schema Duplication

**Critical Finding:** The main schema (`db/schema.sql`) and the commerce schema (`commerce/db/schema.sql`) have overlapping tables:

| Table | Main Schema | Commerce Schema | Conflict |
|-------|-------------|-----------------|----------|
| Products | ✅ `products` | ❌ Not present | Different schemas |
| Leads | ✅ `leads` | ❌ Not present | Different schemas |
| Transactions | ✅ `transactions` | ✅ `payment_transactions` | Different names, same concept |
| Marketplace Listings | ✅ `marketplace_listings` | ❌ Not present | Different schemas |
| Content Templates | ✅ `content_templates` | ❌ Not present | Different schemas |

**Issue:** The two schema files define different tables for the same concepts, and neither references the other. This means the core engine and the commerce module cannot share data directly.

---

## 3. Data Type Analysis

### 3.1 TEXT Fields for JSON Data

Many columns use `TEXT` type to store JSON-serialized data:

| Table | Column | Type | Content |
|-------|--------|------|---------|
| `products` | `features` | TEXT | JSON array of strings |
| `products` | `metadata` | TEXT | JSON object |
| `transactions` | `metadata` | TEXT | JSON object |
| `leads` | `notes` | TEXT | Free text |
| `marketplace_listings` | (various) | TEXT | JSON data |
| `content_templates` | `variables` | TEXT | JSON data |
| `customers` | `billing_profile` | TEXT | JSON data |
| `customers` | `purchase_history` | TEXT | JSON data |
| `customers` | `subscription_history` | TEXT | JSON data |
| `customers` | `license_history` | TEXT | JSON data |
| `customers` | `download_history` | TEXT | JSON data |
| `orders` | `items` | TEXT | JSON array |
| `orders` | `metadata` | TEXT | JSON object |
| `payment_methods` | `metadata` | TEXT | JSON object |
| `payment_transactions` | `metadata` | TEXT | JSON object |
| `payment_providers` | `config` | TEXT | JSON object |
| `payment_providers` | `credentials` | TEXT | JSON object |
| `licenses` | `metadata` | TEXT | JSON object |
| `subscriptions` | `metadata` | TEXT | JSON object |
| `deliveries` | (various) | TEXT | JSON data |
| `invoices` | `metadata` | TEXT | JSON object |
| `receipts` | `metadata` | TEXT | JSON object |
| `coupons` | (various) | TEXT | JSON data |
| `promotions` | `eligibility_rules` | TEXT | JSON data |
| `promotions` | `metadata` | TEXT | JSON object |
| `promotion_rules` | `conditions` | TEXT | JSON data |
| `promotion_rules` | `actions` | TEXT | JSON data |
| `refunds` | `metadata` | TEXT | JSON object |
| `wallets` | (various) | TEXT | JSON data |
| `payouts` | `metadata` | TEXT | JSON object |
| `tax_rules` | (various) | TEXT | JSON data |
| `fraud_events` | `details` | TEXT | JSON data |
| `commerce_events` | `data` | TEXT | JSON data |
| `commerce_audit_log` | `before_data` | TEXT | JSON data |
| `commerce_audit_log` | `after_data` | TEXT | JSON data |
| `commerce_audit_log` | `metadata` | TEXT | JSON object |
| `commerce_metrics` | `value` | TEXT | Any JSON value |
| `commerce_health` | `metrics` | TEXT | JSON data |
| `system_metrics` | (various) | REAL | Numeric |

**Critical Finding:** Over 30 columns store JSON data as TEXT, which prevents:
- Database-level querying of nested fields
- Indexing of JSON properties
- Data type validation at the database level
- Efficient filtering and aggregation

### 3.2 Primary Key Design

Most tables use `TEXT` primary keys with application-generated IDs (UUIDs or custom formats):

```sql
id TEXT PRIMARY KEY  -- Used in most tables
```

**Issue:** TEXT primary keys are less efficient than INTEGER PRIMARY KEY for SQLite. The `system_metrics` table correctly uses `INTEGER PRIMARY KEY AUTOINCREMENT`.

---

## 4. Indexing Analysis

### 4.1 Main Schema Indexes

| Index | Table | Column | Purpose |
|-------|-------|--------|---------|
| `idx_leads_status` | `leads` | `status` | Filter by lead status |
| `idx_leads_country` | `leads` | `country` | Filter by country |
| `idx_leads_created` | `leads` | `created_at` | Sort by creation date |
| `idx_transactions_status` | `transactions` | `status` | Filter by transaction status |
| `idx_transactions_date` | `transactions` | `created_at` | Sort by date |
| `idx_transactions_product` | `transactions` | `product_id` | Join with products |
| `idx_reports_date` | `reports` | `date` | Filter by report date |
| `idx_metrics_timestamp` | `system_metrics` | `timestamp` | Sort by time |
| `idx_listings_product` | `marketplace_listings` | `product_id` | Join with products |
| `idx_listings_marketplace` | `marketplace_listings` | `marketplace` | Filter by marketplace |
| `idx_outreach_lead` | `outreach_log` | `lead_id` | Join with leads |
| `idx_outreach_channel` | `outreach_log` | `channel` | Filter by channel |
| `idx_outreach_sent` | `outreach_log` | `sent_at` | Sort by sent date |

### 4.2 Commerce Schema Indexes

| Index | Table | Column | Purpose |
|-------|-------|--------|---------|
| `idx_customers_email` | `customers` | `email` | Unique lookup |
| `idx_orders_customer` | `orders` | `customer_id` | Join with customers |
| `idx_orders_status` | `orders` | `status` | Filter by status |
| `idx_licenses_customer` | `licenses` | `customer_id` | Join with customers |
| `idx_licenses_product` | `licenses` | `product_id` | Join with products |
| `idx_subscriptions_customer` | `subscriptions` | `customer_id` | Join with customers |
| `idx_deliveries_order` | `deliveries` | `order_id` | Join with orders |
| `idx_invoices_customer` | `invoices` | `customer_id` | Join with customers |
| `idx_refunds_order` | `refunds` | `order_id` | Join with orders |
| `idx_wallets_customer` | `wallets` | `customer_id` | Join with customers |
| `idx_payouts_recipient` | `payouts` | `recipient_id` | Join with recipients |
| `idx_fraud_events_order` | `fraud_events` | `order_id` | Join with orders |
| `idx_commerce_events_type` | `commerce_events` | `event_type` | Filter by event type |
| `idx_audit_log_resource` | `commerce_audit_log` | `resource_type, resource_id` | Composite index |

### 4.3 Missing Indexes

| Missing Index | Impact |
|---------------|--------|
| `outreach_log.response_at` | Slow filtering by response date |
| `transactions.completed_at` | Slow filtering by completion date |
| `leads.source` | Slow filtering by lead source |
| `leads.language` | Slow filtering by language |
| `orders.payment_method` | Slow filtering by payment method |
| `subscriptions.status` | Slow filtering by subscription status |
| `deliveries.download_token` | Slow lookup by token |
| `coupons.code` | Slow coupon validation lookup |
| `fraud_events.customer_id` | Slow fraud lookups by customer |
| `fraud_events.event_type` | Slow fraud lookups by type |
| `commerce_audit_log.action` | Slow audit filtering by action |
| `commerce_audit_log.created_at` | Slow audit filtering by date |
| `commerce_metrics.metric_name` | Slow metric lookups |
| `commerce_health.component_name` | Slow health lookups |

---

## 5. Data Integrity Analysis

### 5.1 Foreign Key Constraints

The main schema has foreign keys on:
- `outreach_log.lead_id → leads.id`
- `marketplace_listings.product_id → products.id`

The commerce schema has foreign keys on:
- `order_items.order_id → orders.order_id`
- `license_activations.license_id → licenses.license_id`
- `subscription_events.subscription_id → subscriptions.id`
- `deliveries.order_id → orders.order_id`
- `invoices.order_id → orders.order_id`
- `refunds.order_id → orders.order_id`
- `wallet_transactions.wallet_id → wallets.id`
- `payouts.recipient_id → wallets.id` (indirectly)
- `promotion_rules.promotion_id → promotions.id`
- `fraud_events.order_id → orders.order_id`

**Issue:** SQLite does not enforce foreign key constraints by default. The `PRAGMA foreign_keys = ON` command must be executed for each connection.

**Evidence:** No `PRAGMA foreign_keys = ON` is found in any `DatabaseManager` or connection setup code.

### 5.2 NOT NULL Constraints

Many important columns lack `NOT NULL` constraints:
- `leads.email` - Nullable (should be NOT NULL)
- `leads.phone` - Nullable
- `transactions.customer_email` - Nullable
- `marketplace_listings.url` - Nullable
- `content_templates.subject` - Nullable

### 5.3 UNIQUE Constraints

Only a few columns have UNIQUE constraints:
- `customers.email` - UNIQUE
- `coupons.code` - UNIQUE
- `invoices.invoice_number` - UNIQUE
- `receipts.receipt_number` - UNIQUE
- `licenses.key` - UNIQUE
- `deliveries.download_token` - UNIQUE

**Missing UNIQUE constraints:**
- `products.id` should be UNIQUE (it's a PRIMARY KEY, so it is)
- `leads.email` should be UNIQUE (it's not)
- `orders.order_id` should be UNIQUE (it's a PRIMARY KEY, so it is)

---

## 6. Connection Management

### 6.1 DatabaseManager Analysis

The `DatabaseManager` at `core/engine.py:169-300` creates a single persistent connection:

```python
def get_connection(self) -> sqlite3.Connection:
    if not self.connection:
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
    return self.connection
```

**Issues:**
1. **No connection pooling** - Single connection shared across all modules
2. **No busy timeout** - SQLite will raise `OperationalError: database is locked` under concurrent access
3. **No WAL mode** - Write operations block read operations
4. **No foreign key enforcement** - `PRAGMA foreign_keys` not set
5. **No connection timeout** - No timeout on connection attempts

### 6.2 Multiple DatabaseManager Instances

Each module creates its own `DatabaseManager` instance:
- `CoreEngine.__init__()` creates one
- `commerce/api/routes.py` creates one at module level
- `marketing-engine/api/routes.py` creates one at module level
- `sales-automation/api/routes.py` creates one at module level

**Result:** 4+ separate connections to the same SQLite file, each with its own cursor and transaction scope.

---

## 7. Migration Support

### Critical Finding: No Migration System

The platform has **no database migration system**. Schema changes require:
1. Manual SQL execution
2. Direct editing of `schema.sql` files
3. No version tracking
4. No rollback capability
5. No migration scripts

**Evidence:** No Alembic, Flyway, or similar migration tool is used. No migration directory exists.

**Violation of GLOBAL_EXECUTION_POLICY.md Section 5.8:**
> "Use transactions for multi-row operations"
> "Connection pooling required"

---

## 8. Backup Strategy

### Current Backup Approach

The `engine.yaml` config mentions:
```yaml
database:
  backup_interval: 86400  # 24 hours
  retention_days: 90
```

However, there is **no backup implementation** in the codebase:
- No `DatabaseManager.backup()` method exists
- The `create_backup_job` in `scheduler.py:319-332` references `db_manager.backup()` which doesn't exist
- No backup files are created

**Evidence:** `scheduler/scheduler.py:319-332` - `create_backup_job()` calls `db_manager.backup()` which is not implemented

---

## 9. Database Security

### 9.1 Encryption at Rest

SQLite databases are **unencrypted** by default. The `cryptography` library is available (listed in `requirements.txt`) but not used for database encryption.

**Violation of GLOBAL_EXECUTION_POLICY.md Section 8.3:**
> "Encrypt sensitive data at rest"

### 9.2 Access Control

SQLite file-based access control depends on OS-level file permissions. There is no:
- Database-level user authentication
- Row-level security
- Column-level encryption
- Access control lists

### 9.3 SQL Injection Prevention

The codebase uses parameterized queries in most places:
```python
cursor.execute("SELECT * FROM products WHERE status = ?", (status,))
```

However, some dynamic SQL construction exists in `product-factory/core/factory.py`:
```python
cursor.execute(f"UPDATE pf_products SET {set_clause} WHERE id = ?", values)
```

While this uses parameterized values for the WHERE clause, the SET clause is dynamically constructed, which could be vulnerable if `set_clause` is user-controlled.

---

## 10. Recommendations

1. **Consolidate schemas** - Merge `db/schema.sql` and `commerce/db/schema.sql` into a single unified schema
2. **Add PRAGMA foreign_keys = ON** to all database connections
3. **Enable WAL mode** for better concurrent access
4. **Add a busy timeout** to SQLite connections (e.g., `timeout=30`)
5. **Implement a migration system** (Alembic or custom)
6. **Add missing indexes** for common query patterns
7. **Implement backup functionality** in `DatabaseManager`
8. **Add database encryption** using SQLCipher or application-level encryption
9. **Replace TEXT JSON columns** with proper JSON types or separate normalized tables
10. **Add NOT NULL constraints** to all required columns
11. **Add UNIQUE constraints** to all unique columns
12. **Implement connection pooling** instead of single persistent connections
13. **Add database query logging** for performance monitoring
14. **Add database health checks** that verify connectivity and schema integrity

---

*End of Database Review*