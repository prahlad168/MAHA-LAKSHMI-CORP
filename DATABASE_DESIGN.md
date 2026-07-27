# DATABASE DESIGN - MAHA SALES ENGINE V1

**Version:** 1.0.0  
**Status:** Approved  
**Parent Document:** MASTER_BLUEPRINT.md, SYSTEM_ARCHITECTURE.md  
**Created:** 2026-07-27

---

## 1. Database Technology

**SQLite** - File-based relational database.

### Rationale
- Zero configuration
- Portable (single file)
- No server required
- Full SQL support
- ACID compliant
- Perfect for single-node deployment

---

## 2. Database Location

```
maha-sales-engine/
└── db/
    └── maha_sales_engine.db    # Primary database
    └── backups/
        └── maha_sales_engine_2026-07-27.db    # Daily backups
```

Configurable via `config/engine.yaml`:
```yaml
database:
  path: "./db/maha_sales_engine.db"
  backup_interval: 86400
  retention_days: 90
```

---

## 3. Entity Relationship Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   products  │     │    leads    │     │  outreach_log │
├─────────────┤     ├─────────────┤     ├─────────────┤
│ id (PK)     │     │ id (PK)     │     │ id (PK)     │
│ name        │     │ name        │     │ lead_id (FK)│
│ description │     │ email       │     │ channel     │
│ price_usd   │     │ phone       │     │ template_type│
│ price_idr   │     │ company     │     │ content     │
│ category    │     │ industry    │     │ status      │
│ features    │     │ country     │     │ sent_at     │
│ status      │     │ language    │     │ response_at │
│ created_at  │     │ source      │     └─────────────┘
│ updated_at  │     │ status      │
└─────────────┘     │ score       │     ┌─────────────┐
       │            │ created_at  │     │ transactions│
       │            │ last_contact│     ├─────────────┤
       │            │ followup_count│   │ id (PK)     │
       │            └─────────────┘     │ gateway     │
       │                   │            │ customer_email│
       │                   │            │ customer_name│
       │                   │            │ amount      │
       │                   │            │ currency    │
       │                   │            │ product_id  │
       │                   │            │ status      │
       │                   │            │ payment_method│
       │                   │            │ created_at  │
       │                   │            │ completed_at│
       │                   │            └─────────────┘
       │                   │                   │
       │                   │                   │
       └───────────────────┴───────────────────┘
                           │
                           │
                    ┌─────────────┐     ┌─────────────┐
                    │   reports   │     │system_metrics│
                    ├─────────────┤     ├─────────────┤
                    │ id (PK)     │     │ id (PK)     │
                    │ report_type │     │ timestamp   │
                    │ date        │     │ cpu_usage   │
                    │ data        │     │ memory_usage│
                    │ created_at  │     │ disk_usage  │
                    └─────────────┘     │ active_leads│
                                        │ queue_size  │
                                        └─────────────┘

                    ┌─────────────────────────────────┐
                    │     marketplace_listings        │
                    ├─────────────────────────────────┤
                    │ id (PK)                         │
                    │ product_id (FK)                 │
                    │ marketplace                     │
                    │ status                          │
                    │ url                             │
                    │ price                           │
                    │ currency                        │
                    │ views                           │
                    │ sales                           │
                    │ reviews                         │
                    │ rating                          │
                    │ last_synced                     │
                    │ created_at                      │
                    └─────────────────────────────────┘
```

---

## 4. Table Definitions

### 4.1 products
Stores digital product catalog.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | Unique product identifier |
| name | TEXT | NOT NULL | Product display name |
| description | TEXT | | Full product description |
| price_usd | REAL | | Price in USD |
| price_idr | REAL | | Price in IDR |
| category | TEXT | | Product category |
| features | TEXT | | JSON array of features |
| status | TEXT | DEFAULT 'active' | draft/active/paused/archived |
| created_at | TEXT | | ISO timestamp |
| updated_at | TEXT | | ISO timestamp |

**Indexes:**
- None required for this table size

---

### 4.2 leads
Stores sales leads.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | Unique lead identifier |
| name | TEXT | NOT NULL | Contact name |
| email | TEXT | | Email address |
| phone | TEXT | | Phone number |
| company | TEXT | | Company name |
| industry | TEXT | | Industry category |
| country | TEXT | | Country name |
| language | TEXT | | Preferred language |
| source | TEXT | | Lead source |
| status | TEXT | DEFAULT 'new' | new/contacted/responded/proposal/closed |
| score | INTEGER | DEFAULT 0 | Lead quality score |
| created_at | TEXT | | ISO timestamp |
| last_contact | TEXT | | ISO timestamp |
| followup_count | INTEGER | DEFAULT 0 | Number of follow-ups |
| notes | TEXT | | Additional notes |

**Indexes:**
- `idx_leads_status` ON status
- `idx_leads_country` ON country
- `idx_leads_created` ON created_at

---

### 4.3 outreach_log
Logs all outreach activities.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | Unique log entry ID |
| lead_id | TEXT | FK → leads.id | Associated lead |
| channel | TEXT | NOT NULL | email/whatsapp/linkedin |
| template_type | TEXT | | Template used |
| content | TEXT | | Message content |
| status | TEXT | DEFAULT 'sent' | sent/delivered/read/failed |
| sent_at | TEXT | | ISO timestamp |
| response_received | INTEGER | DEFAULT 0 | 0/1 flag |
| response_at | TEXT | | ISO timestamp |

**Indexes:**
- `idx_outreach_lead` ON lead_id
- `idx_outreach_channel` ON channel
- `idx_outreach_sent` ON sent_at

---

### 4.4 transactions
Records all financial transactions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | Unique transaction ID |
| gateway | TEXT | NOT NULL | Payment gateway name |
| customer_email | TEXT | | Customer email |
| customer_name | TEXT | | Customer name |
| amount | REAL | NOT NULL | Transaction amount |
| currency | TEXT | NOT NULL | USD/IDR/etc |
| fee_amount | REAL | DEFAULT 0.0 | Gateway fee |
| net_amount | REAL | NOT NULL | Amount after fees |
| product_id | TEXT | | Associated product |
| status | TEXT | DEFAULT 'pending' | pending/completed/failed/refunded |
| payment_method | TEXT | | Payment method used |
| created_at | TEXT | | ISO timestamp |
| completed_at | TEXT | | ISO timestamp |
| metadata | TEXT | | JSON metadata |

**Indexes:**
- `idx_transactions_status` ON status
- `idx_transactions_date` ON created_at
- `idx_transactions_product` ON product_id

---

### 4.5 payouts
Records profit distributions to CEO.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | Unique payout ID |
| amount | REAL | NOT NULL | Payout amount |
| currency | TEXT | NOT NULL | Currency |
| destination | TEXT | NOT NULL | Bank account / wallet |
| destination_type | TEXT | NOT NULL | bank/crypto/wallet |
| status | TEXT | DEFAULT 'pending' | pending/processing/completed/failed |
| fee_amount | REAL | DEFAULT 0.0 | Transfer fee |
| net_amount | REAL | NOT NULL | Net amount received |
| created_at | TEXT | | ISO timestamp |
| completed_at | TEXT | | ISO timestamp |
| reference | TEXT | | Reference transaction |

---

### 4.6 reports
Stores generated reports.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | Unique report ID |
| report_type | TEXT | NOT NULL | daily/weekly/monthly/custom |
| date | TEXT | NOT NULL | Report date |
| data | TEXT | NOT NULL | JSON report data |
| created_at | TEXT | | ISO timestamp |

**Indexes:**
- `idx_reports_date` ON date

---

### 4.7 system_metrics
Stores system performance metrics.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Row ID |
| timestamp | TEXT | NOT NULL | ISO timestamp |
| cpu_usage | REAL | | CPU percentage |
| memory_usage | REAL | | Memory percentage |
| disk_usage | REAL | | Disk percentage |
| active_leads | INTEGER | | Current active leads |
| queue_size | INTEGER | | Pending jobs |

**Indexes:**
- `idx_metrics_timestamp` ON timestamp

---

### 4.8 marketplace_listings
Tracks product listings across marketplaces.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | Unique listing ID |
| product_id | TEXT | FK → products.id | Associated product |
| marketplace | TEXT | NOT NULL | gumroad/shopify/etsy/etc |
| status | TEXT | DEFAULT 'draft' | draft/published/paused/archived |
| url | TEXT | | Listing URL |
| price | REAL | | Listed price |
| currency | TEXT | DEFAULT 'USD' | Currency |
| views | INTEGER | DEFAULT 0 | View count |
| sales | INTEGER | DEFAULT 0 | Sales count |
| reviews | INTEGER | DEFAULT 0 | Review count |
| rating | REAL | DEFAULT 0.0 | Average rating |
| last_synced | TEXT | | ISO timestamp |
| created_at | TEXT | | ISO timestamp |

**Indexes:**
- `idx_listings_product` ON product_id
- `idx_listings_marketplace` ON marketplace

---

### 4.9 content_templates
Stores content templates for outreach.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PRIMARY KEY | Unique template ID |
| template_type | TEXT | NOT NULL | email/whatsapp/linkedin |
| language | TEXT | NOT NULL | Language code |
| subject | TEXT | | Email subject |
| body | TEXT | | Template body |
| variables | TEXT | | JSON variable list |
| performance_score | REAL | DEFAULT 0.0 | A/B test score |
| usage_count | INTEGER | DEFAULT 0 | Times used |
| created_at | TEXT | | ISO timestamp |

---

## 5. Data Retention

| Table | Retention | Reason |
|-------|-----------|--------|
| products | Indefinite | Product catalog |
| leads | 90 days | GDPR compliance |
| outreach_log | 90 days | GDPR compliance |
| transactions | 7 years | Financial records |
| payouts | 7 years | Financial records |
| reports | 1 year | Analytics history |
| system_metrics | 30 days | Performance trending |
| marketplace_listings | Indefinite | Product listings |
| content_templates | Indefinite | Asset library |

Automated cleanup runs daily via Scheduler.

---

## 6. Backup Strategy

- **Frequency:** Daily at 02:00 local time
- **Location:** `db/backups/`
- **Naming:** `maha_sales_engine_YYYY-MM-DD.db`
- **Retention:** 90 days
- **Method:** File copy with compression

---

## 7. Migration Strategy

- Schema version tracked in `reports` table
- Migrations applied on engine startup
- Backward compatible only
- No destructive migrations in V1

---

## 8. Performance Considerations

- All queries use indexes
- No full table scans in production paths
- Connection pooling via singleton `DatabaseManager`
- WAL mode for SQLite (if supported)
- Regular VACUUM after large deletions

---

## 9. Security

- Database file permissions: owner read/write only
- No sensitive data stored in plaintext (use encryption for PII)
- Backup files compressed and optionally encrypted
- No SQL injection vectors (parameterized queries only)

---

**Approved By:** CEO / Lead Architect  
**Date:** 2026-07-27  
**Next Review:** 2026-08-27
