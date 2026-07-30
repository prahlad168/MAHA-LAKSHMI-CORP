-- MAHA SALES ENGINE V1 - Marketplace Connector Database Schema
-- Revenue Sprint 1 Database Migration

-- Marketplace Accounts
CREATE TABLE IF NOT EXISTS marketplace_accounts (
    account_id TEXT PRIMARY KEY,
    provider TEXT NOT NULL,
    name TEXT NOT NULL,
    credentials TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    default INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    last_sync TEXT,
    token_expires_at TEXT
);

-- Marketplace Products
CREATE TABLE IF NOT EXISTS marketplace_products (
    product_id TEXT PRIMARY KEY,
    internal_product_id TEXT NOT NULL,
    marketplace_product_id TEXT,
    marketplace_url TEXT,
    status TEXT NOT NULL,
    provider TEXT NOT NULL,
    price REAL NOT NULL,
    currency TEXT NOT NULL,
    visibility TEXT NOT NULL,
    published_at TEXT,
    updated_at TEXT NOT NULL,
    checksum TEXT,
    metadata TEXT
);

-- Marketplace Publications
CREATE TABLE IF NOT EXISTS marketplace_publications (
    publication_id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    account_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    status TEXT NOT NULL,
    current_stage TEXT NOT NULL,
    stages_completed TEXT NOT NULL,
    errors TEXT NOT NULL,
    data TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    published_at TEXT
);

-- Publication History
CREATE TABLE IF NOT EXISTS publication_history (
    history_id TEXT PRIMARY KEY,
    publication_id TEXT NOT NULL,
    action TEXT NOT NULL,
    stage TEXT NOT NULL,
    status TEXT NOT NULL,
    message TEXT,
    data TEXT,
    created_at TEXT NOT NULL
);

-- Publication Logs
CREATE TABLE IF NOT EXISTS publication_logs (
    log_id TEXT PRIMARY KEY,
    publication_id TEXT NOT NULL,
    level TEXT NOT NULL,
    message TEXT NOT NULL,
    data TEXT,
    created_at TEXT NOT NULL
);

-- Publication Errors
CREATE TABLE IF NOT EXISTS publication_errors (
    error_id TEXT PRIMARY KEY,
    publication_id TEXT NOT NULL,
    stage TEXT NOT NULL,
    error_code TEXT,
    message TEXT NOT NULL,
    stack_trace TEXT,
    resolved INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

-- Marketplace Webhooks
CREATE TABLE IF NOT EXISTS marketplace_webhooks (
    webhook_id TEXT PRIMARY KEY,
    provider TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload TEXT NOT NULL,
    signature TEXT NOT NULL,
    processed INTEGER NOT NULL DEFAULT 0,
    processed_at TEXT,
    created_at TEXT NOT NULL
);

-- Sync Jobs
CREATE TABLE IF NOT EXISTS sync_jobs (
    job_id TEXT PRIMARY KEY,
    sync_type TEXT NOT NULL,
    provider TEXT NOT NULL,
    status TEXT NOT NULL,
    products_synced INTEGER NOT NULL,
    products_failed INTEGER NOT NULL,
    errors TEXT NOT NULL,
    started_at TEXT,
    completed_at TEXT,
    created_at TEXT NOT NULL
);

-- Provider Configuration
CREATE TABLE IF NOT EXISTS provider_configuration (
    config_id TEXT PRIMARY KEY,
    provider TEXT NOT NULL,
    config_key TEXT NOT NULL,
    config_value TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Provider Tokens
CREATE TABLE IF NOT EXISTS provider_tokens (
    token_id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    expires_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Publication Metrics
CREATE TABLE IF NOT EXISTS publication_metrics (
    metric_id TEXT PRIMARY KEY,
    provider TEXT NOT NULL,
    date TEXT NOT NULL,
    total_publications INTEGER NOT NULL,
    successful_publications INTEGER NOT NULL,
    failed_publications INTEGER NOT NULL,
    avg_publication_time REAL NOT NULL,
    created_at TEXT NOT NULL
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_marketplace_products_status ON marketplace_products(status);
CREATE INDEX IF NOT EXISTS idx_marketplace_products_provider ON marketplace_products(provider);
CREATE INDEX IF NOT EXISTS idx_marketplace_publications_status ON marketplace_publications(status);
CREATE INDEX IF NOT EXISTS idx_publication_history_publication ON publication_history(publication_id);
CREATE INDEX IF NOT EXISTS idx_publication_errors_publication ON publication_errors(publication_id);
CREATE INDEX IF NOT EXISTS idx_sync_jobs_status ON sync_jobs(status);
CREATE INDEX IF NOT EXISTS idx_provider_tokens_account ON provider_tokens(account_id);
CREATE INDEX IF NOT EXISTS idx_publication_metrics_date ON publication_metrics(date);
