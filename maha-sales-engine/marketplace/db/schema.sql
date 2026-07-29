-- MAHA SALES ENGINE V1 - Marketplace Database Schema
-- SQLite Database

-- Marketplaces table
CREATE TABLE IF NOT EXISTS marketplaces (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    provider TEXT NOT NULL,
    version TEXT DEFAULT '1.0.0',
    status TEXT DEFAULT 'active',
    capabilities TEXT,
    auth_type TEXT DEFAULT 'api_key',
    config TEXT,
    created_at TEXT,
    updated_at TEXT
);

-- Marketplace plugins table
CREATE TABLE IF NOT EXISTS marketplace_plugins (
    id TEXT PRIMARY KEY,
    marketplace_id TEXT NOT NULL,
    plugin_name TEXT NOT NULL,
    plugin_version TEXT NOT NULL,
    enabled BOOLEAN DEFAULT 1,
    config TEXT,
    installed_at TEXT,
    updated_at TEXT,
    FOREIGN KEY (marketplace_id) REFERENCES marketplaces (id)
);

-- Marketplace credentials table
CREATE TABLE IF NOT EXISTS marketplace_credentials (
    id TEXT PRIMARY KEY,
    marketplace_id TEXT NOT NULL,
    credential_type TEXT NOT NULL,
    encrypted_data TEXT NOT NULL,
    is_encrypted BOOLEAN DEFAULT 1,
    last_rotated TEXT,
    expires_at TEXT,
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY (marketplace_id) REFERENCES marketplaces (id)
);

-- Marketplace products table
CREATE TABLE IF NOT EXISTS marketplace_products (
    mapping_id TEXT PRIMARY KEY,
    marketplace_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    marketplace_product_id TEXT,
    listing_id TEXT,
    external_url TEXT,
    published_version TEXT,
    publication_status TEXT DEFAULT 'draft',
    last_sync TEXT,
    last_error TEXT,
    retry_count INTEGER DEFAULT 0,
    metadata TEXT,
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY (marketplace_id) REFERENCES marketplaces (id)
);

-- Publication jobs table
CREATE TABLE IF NOT EXISTS publication_jobs (
    id TEXT PRIMARY KEY,
    marketplace_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    action TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    priority TEXT DEFAULT 'normal',
    parameters TEXT,
    result TEXT,
    error_message TEXT,
    created_at TEXT,
    started_at TEXT,
    completed_at TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    FOREIGN KEY (marketplace_id) REFERENCES marketplaces (id)
);

-- Publication history table
CREATE TABLE IF NOT EXISTS publication_history (
    id TEXT PRIMARY KEY,
    marketplace_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    action TEXT NOT NULL,
    status TEXT NOT NULL,
    request_data TEXT,
    response_data TEXT,
    error_message TEXT,
    duration_ms INTEGER,
    created_at TEXT,
    FOREIGN KEY (marketplace_id) REFERENCES marketplaces (id)
);

-- Provider capabilities table
CREATE TABLE IF NOT EXISTS provider_capabilities (
    id TEXT PRIMARY KEY,
    provider_name TEXT NOT NULL,
    capability_name TEXT NOT NULL,
    description TEXT,
    supported BOOLEAN DEFAULT 1,
    created_at TEXT
);

-- Provider versions table
CREATE TABLE IF NOT EXISTS provider_versions (
    id TEXT PRIMARY KEY,
    provider_name TEXT NOT NULL,
    version TEXT NOT NULL,
    manifest TEXT,
    is_current BOOLEAN DEFAULT 1,
    created_at TEXT
);

-- Event log table
CREATE TABLE IF NOT EXISTS event_log (
    id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    source TEXT DEFAULT 'marketplace',
    event_id TEXT NOT NULL,
    data TEXT NOT NULL,
    created_at TEXT
);

-- Audit log table
CREATE TABLE IF NOT EXISTS marketplace_audit_log (
    id TEXT PRIMARY KEY,
    action TEXT NOT NULL,
    marketplace_id TEXT NOT NULL,
    product_id TEXT,
    before_data TEXT,
    after_data TEXT,
    ip_address TEXT,
    result TEXT DEFAULT 'success',
    user_id TEXT DEFAULT 'system',
    created_at TEXT
);

-- Job queue table
CREATE TABLE IF NOT EXISTS job_queue (
    id TEXT PRIMARY KEY,
    job_type TEXT NOT NULL,
    priority TEXT DEFAULT 'normal',
    state TEXT DEFAULT 'pending',
    payload TEXT NOT NULL,
    result TEXT,
    error_message TEXT,
    created_at TEXT,
    started_at TEXT,
    completed_at TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    timeout INTEGER DEFAULT 300
);

-- Webhook logs table
CREATE TABLE IF NOT EXISTS webhook_logs (
    id TEXT PRIMARY KEY,
    marketplace_id TEXT NOT NULL,
    payload TEXT NOT NULL,
    status TEXT DEFAULT 'received',
    processed BOOLEAN DEFAULT 0,
    error_message TEXT,
    received_at TEXT,
    processed_at TEXT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_marketplaces_status ON marketplaces(status);
CREATE INDEX IF NOT EXISTS idx_marketplaces_provider ON marketplaces(provider);
CREATE INDEX IF NOT EXISTS idx_products_marketplace ON marketplace_products(marketplace_id);
CREATE INDEX IF NOT EXISTS idx_products_status ON marketplace_products(publication_status);
CREATE INDEX IF NOT EXISTS idx_jobs_state ON publication_jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_marketplace ON publication_jobs(marketplace_id);
CREATE INDEX IF NOT EXISTS idx_audit_marketplace ON marketplace_audit_log(marketplace_id);
CREATE INDEX IF NOT EXISTS idx_audit_created ON marketplace_audit_log(created_at);
CREATE INDEX IF NOT EXISTS idx_webhooks_marketplace ON webhook_logs(marketplace_id);
CREATE INDEX IF NOT EXISTS idx_event_type ON event_log(event_type);

-- Default provider capabilities
INSERT OR IGNORE INTO provider_capabilities (id, provider_name, capability_name, description, supported, created_at)
VALUES 
    ('cap-draft', 'gumroad', 'supports_draft', 'Supports draft publications', 1, '2026-07-27'),
    ('cap-update', 'gumroad', 'supports_update', 'Supports updating publications', 1, '2026-07-27'),
    ('cap-delete', 'gumroad', 'supports_delete', 'Supports deleting publications', 1, '2026-07-27'),
    ('cap-variants', 'gumroad', 'supports_variants', 'Supports product variants', 1, '2026-07-27'),
    ('cap-preview', 'gumroad', 'supports_preview', 'Supports preview images', 1, '2026-07-27'),
    ('cap-draft', 'etsy', 'supports_draft', 'Supports draft publications', 1, '2026-07-27'),
    ('cap-update', 'etsy', 'supports_update', 'Supports updating publications', 1, '2026-07-27'),
    ('cap-tags', 'etsy', 'supports_tags', 'Supports tags', 1, '2026-07-27'),
    ('cap-categories', 'etsy', 'supports_categories', 'Supports categories', 1, '2026-07-27');
