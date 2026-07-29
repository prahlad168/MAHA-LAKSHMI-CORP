-- Revenue Sprint 3: durable product-generation queue and product catalog.
-- This migration deliberately remains SQLite-compatible; PostgreSQL is handled
-- as a deployment target only after the existing SQLite migrations are ported.

CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    price REAL NOT NULL DEFAULT 0,
    currency TEXT NOT NULL DEFAULT 'USD',
    category TEXT,
    tags TEXT NOT NULL DEFAULT '[]',
    status TEXT NOT NULL DEFAULT 'draft',
    content TEXT,
    created_by TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS marketplace_accounts (
    id TEXT PRIMARY KEY,
    provider TEXT NOT NULL,
    name TEXT NOT NULL,
    api_key TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    last_sync_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS marketplace_products (
    id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    account_id TEXT NOT NULL,
    marketplace_product_id TEXT,
    marketplace_url TEXT,
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (account_id) REFERENCES marketplace_accounts(id)
);

CREATE TABLE IF NOT EXISTS marketplace_publications (
    id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    account_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    status TEXT NOT NULL,
    marketplace_product_id TEXT,
    marketplace_url TEXT,
    response_data TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (account_id) REFERENCES marketplace_accounts(id)
);

-- 005 created the queue before ownership and retry fields existed.
ALTER TABLE product_generation_jobs ADD COLUMN created_by TEXT;
ALTER TABLE product_generation_jobs ADD COLUMN started_at TEXT;
ALTER TABLE product_generation_jobs ADD COLUMN completed_at TEXT;
ALTER TABLE product_generation_jobs ADD COLUMN attempts INTEGER NOT NULL DEFAULT 0;

CREATE INDEX IF NOT EXISTS idx_products_status_created_at ON products(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_product_jobs_status_created_at ON product_generation_jobs(status, created_at);
CREATE INDEX IF NOT EXISTS idx_product_jobs_worker_status ON product_generation_jobs(worker_id, status);
CREATE INDEX IF NOT EXISTS idx_marketplace_publications_product_status ON marketplace_publications(product_id, status);
