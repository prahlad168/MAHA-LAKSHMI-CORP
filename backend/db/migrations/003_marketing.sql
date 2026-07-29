-- Migration 003: Marketing tables
CREATE TABLE IF NOT EXISTS marketing_campaigns (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    budget REAL,
    spent REAL DEFAULT 0,
    start_date TEXT,
    end_date TEXT,
    metadata TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS content_assets (
    id TEXT PRIMARY KEY,
    campaign_id TEXT,
    type TEXT NOT NULL,
    title TEXT,
    content TEXT,
    status TEXT NOT NULL DEFAULT 'draft',
    seo_score INTEGER,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (campaign_id) REFERENCES marketing_campaigns(id)
);

CREATE TABLE IF NOT EXISTS ab_tests (
    id TEXT PRIMARY KEY,
    campaign_id TEXT,
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'running',
    variant_a TEXT,
    variant_b TEXT,
    winner TEXT,
    confidence REAL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (campaign_id) REFERENCES marketing_campaigns(id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON marketing_campaigns(status);
CREATE INDEX IF NOT EXISTS idx_ab_tests_status ON ab_tests(status);
