-- MAHA SALES ENGINE V1 - Product Factory Database Schema
-- SQLite Database

-- Products table
CREATE TABLE IF NOT EXISTS pf_products (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL,
    status TEXT DEFAULT 'idea',
    license_type TEXT DEFAULT 'personal',
    price_usd REAL DEFAULT 0.0,
    price_idr REAL DEFAULT 0.0,
    author TEXT DEFAULT 'MAHA LAKSHMI',
    tags TEXT,
    target_market TEXT,
    language TEXT DEFAULT 'en',
    file_path TEXT,
    preview_path TEXT,
    thumbnail_path TEXT,
    version_count INTEGER DEFAULT 0,
    download_count INTEGER DEFAULT 0,
    rating REAL DEFAULT 0.0,
    review_count INTEGER DEFAULT 0,
    created_at TEXT,
    updated_at TEXT,
    archived_at TEXT
);

-- Product versions table
CREATE TABLE IF NOT EXISTS pf_product_versions (
    id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    version_number TEXT NOT NULL,
    created_at TEXT,
    created_by TEXT,
    changelog TEXT,
    file_path TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    file_size INTEGER,
    metadata TEXT,
    FOREIGN KEY (product_id) REFERENCES pf_products (id)
);

-- Product categories table
CREATE TABLE IF NOT EXISTS pf_product_categories (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    icon TEXT,
    created_at TEXT
);

-- Product keywords table
CREATE TABLE IF NOT EXISTS pf_product_keywords (
    id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    keyword TEXT NOT NULL,
    language TEXT DEFAULT 'en',
    search_volume INTEGER DEFAULT 0,
    competition TEXT DEFAULT 'medium',
    created_at TEXT,
    FOREIGN KEY (product_id) REFERENCES pf_products (id)
);

-- Licenses table
CREATE TABLE IF NOT EXISTS pf_licenses (
    id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    license_type TEXT NOT NULL,
    terms TEXT,
    restrictions TEXT,
    created_at TEXT,
    FOREIGN KEY (product_id) REFERENCES pf_products (id)
);

-- Quality reports table
CREATE TABLE IF NOT EXISTS pf_quality_reports (
    id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    version_id TEXT NOT NULL,
    created_at TEXT,
    overall_score REAL,
    checks TEXT NOT NULL,
    passed BOOLEAN DEFAULT 0,
    issues TEXT,
    FOREIGN KEY (product_id) REFERENCES pf_products (id),
    FOREIGN KEY (version_id) REFERENCES pf_product_versions (id)
);

-- Generation jobs table
CREATE TABLE IF NOT EXISTS pf_generation_jobs (
    id TEXT PRIMARY KEY,
    product_id TEXT,
    status TEXT DEFAULT 'pending',
    created_at TEXT,
    started_at TEXT,
    completed_at TEXT,
    generator_type TEXT,
    parameters TEXT,
    result_path TEXT,
    error_message TEXT,
    logs TEXT,
    FOREIGN KEY (product_id) REFERENCES pf_products (id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_pf_products_status ON pf_products(status);
CREATE INDEX IF NOT EXISTS idx_pf_products_category ON pf_products(category);
CREATE INDEX IF NOT EXISTS idx_pf_products_created ON pf_products(created_at);
CREATE INDEX IF NOT EXISTS idx_pf_versions_product ON pf_product_versions(product_id);
CREATE INDEX IF NOT EXISTS idx_pf_keywords_product ON pf_product_keywords(product_id);
CREATE INDEX IF NOT EXISTS idx_pf_jobs_status ON pf_generation_jobs(status);

-- Default categories
INSERT OR IGNORE INTO pf_product_categories (id, name, description, icon, created_at)
VALUES 
    ('cat-ebook', 'eBook', 'Digital book in PDF format', '📚', '2026-07-27'),
    ('cat-prompt-pack', 'Prompt Pack', 'Collection of AI prompts', '🤖', '2026-07-27'),
    ('cat-template', 'Template', 'Ready-to-use templates', '📄', '2026-07-27'),
    ('cat-checklist', 'Checklist', 'Actionable checklists', '✅', '2026-07-27'),
    ('cat-mini-course', 'Mini Course', 'Structured learning content', '🎓', '2026-07-27');
