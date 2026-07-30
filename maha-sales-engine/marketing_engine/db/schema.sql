-- MAHA SALES ENGINE V1 - Marketing Database Schema
-- SQLite Database

-- Marketing assets table
CREATE TABLE IF NOT EXISTS marketing_assets (
    id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    content_type TEXT NOT NULL,
    locale TEXT DEFAULT 'en',
    content TEXT,
    metadata TEXT,
    status TEXT DEFAULT 'draft',
    version TEXT DEFAULT '1.0.0',
    approved_by TEXT DEFAULT 'system',
    approved_at TEXT,
    created_at TEXT,
    updated_at TEXT
);

-- SEO assets table
CREATE TABLE IF NOT EXISTS seo_assets (
    id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    title TEXT,
    description TEXT,
    slug TEXT,
    canonical_url TEXT,
    meta_keywords TEXT,
    og_title TEXT,
    og_description TEXT,
    og_image TEXT,
    twitter_title TEXT,
    twitter_description TEXT,
    twitter_image TEXT,
    schema_org TEXT,
    alt_texts TEXT,
    internal_links TEXT,
    created_at TEXT,
    updated_at TEXT
);

-- Keywords table
CREATE TABLE IF NOT EXISTS keywords (
    id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    keyword TEXT NOT NULL,
    intent TEXT DEFAULT 'transactional',
    difficulty TEXT DEFAULT 'medium',
    priority TEXT DEFAULT 'medium',
    search_volume INTEGER DEFAULT 0,
    competition TEXT DEFAULT 'medium',
    language TEXT DEFAULT 'en',
    category TEXT,
    related_keywords TEXT,
    created_at TEXT
);

-- Hashtags table
CREATE TABLE IF NOT EXISTS hashtags (
    id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    platform TEXT NOT NULL,
    hashtag TEXT NOT NULL,
    usage_count INTEGER DEFAULT 0,
    created_at TEXT
);

-- Campaign templates table
CREATE TABLE IF NOT EXISTS campaign_templates (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    content_type TEXT NOT NULL,
    template TEXT NOT NULL,
    variables TEXT,
    tags TEXT,
    is_active BOOLEAN DEFAULT 1,
    usage_count INTEGER DEFAULT 0,
    created_at TEXT,
    updated_at TEXT
);

-- Prompt library table
CREATE TABLE IF NOT EXISTS prompt_library (
    prompt_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    version TEXT NOT NULL,
    content TEXT NOT NULL,
    variables TEXT,
    description TEXT,
    tags TEXT,
    created_at TEXT,
    updated_at TEXT,
    author TEXT DEFAULT 'system',
    parent_id TEXT,
    is_active BOOLEAN DEFAULT 1,
    usage_count INTEGER DEFAULT 0,
    success_rate REAL DEFAULT 0.0
);

-- Prompt versions table
CREATE TABLE IF NOT EXISTS prompt_versions (
    id TEXT PRIMARY KEY,
    prompt_id TEXT NOT NULL,
    version TEXT NOT NULL,
    content TEXT NOT NULL,
    changelog TEXT,
    created_at TEXT,
    created_by TEXT,
    FOREIGN KEY (prompt_id) REFERENCES prompt_library (prompt_id)
);

-- Content versions table
CREATE TABLE IF NOT EXISTS content_versions (
    id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    content_type TEXT NOT NULL,
    version TEXT NOT NULL,
    content TEXT,
    status TEXT DEFAULT 'draft',
    changelog TEXT,
    created_at TEXT,
    created_by TEXT
);

-- A/B tests table
CREATE TABLE IF NOT EXISTS ab_tests (
    test_id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    content_type TEXT NOT NULL,
    status TEXT DEFAULT 'draft',
    variants TEXT NOT NULL,
    metrics TEXT,
    winner TEXT,
    created_at TEXT,
    completed_at TEXT
);

-- Brand rules table
CREATE TABLE IF NOT EXISTS brand_rules (
    brand_name TEXT PRIMARY KEY,
    voice TEXT,
    tone TEXT,
    writing_style TEXT,
    forbidden_terms TEXT,
    preferred_terms TEXT,
    legal_requirements TEXT,
    target_audience TEXT,
    value_proposition TEXT,
    usp TEXT,
    created_at TEXT,
    updated_at TEXT
);

-- Audiences table
CREATE TABLE IF NOT EXISTS audiences (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    demographics TEXT,
    interests TEXT,
    pain_points TEXT,
    goals TEXT,
    created_at TEXT
);

-- Competitor profiles table
CREATE TABLE IF NOT EXISTS competitor_profiles (
    id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    competitor_name TEXT NOT NULL,
    strengths TEXT,
    weaknesses TEXT,
    pricing_strategy TEXT,
    market_position TEXT,
    created_at TEXT
);

-- Localized content table
CREATE TABLE IF NOT EXISTS localized_content (
    content_id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    content_type TEXT NOT NULL,
    language TEXT NOT NULL,
    region TEXT,
    currency TEXT,
    culture TEXT,
    content TEXT,
    translation_version TEXT,
    is_machine_translated BOOLEAN DEFAULT 1,
    reviewed BOOLEAN DEFAULT 0,
    created_at TEXT
);

-- Asset specs table
CREATE TABLE IF NOT EXISTS asset_specs (
    asset_id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    asset_type TEXT NOT NULL,
    title TEXT,
    description TEXT,
    dimensions TEXT,
    format TEXT,
    style TEXT,
    colors TEXT,
    text_elements TEXT,
    generated_image TEXT,
    created_at TEXT
);

-- Marketing event log table
CREATE TABLE IF NOT EXISTS marketing_event_log (
    id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    source TEXT DEFAULT 'marketing',
    event_id TEXT NOT NULL,
    data TEXT NOT NULL,
    created_at TEXT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_marketing_assets_product ON marketing_assets(product_id);
CREATE INDEX IF NOT EXISTS idx_marketing_assets_type ON marketing_assets(content_type);
CREATE INDEX IF NOT EXISTS idx_seo_assets_product ON seo_assets(product_id);
CREATE INDEX IF NOT EXISTS idx_keywords_product ON keywords(product_id);
CREATE INDEX IF NOT EXISTS idx_keywords_language ON keywords(language);
CREATE INDEX IF NOT EXISTS idx_hashtags_product ON hashtags(product_id);
CREATE INDEX IF NOT EXISTS idx_ab_tests_product ON ab_tests(product_id);
CREATE INDEX IF NOT EXISTS idx_prompt_category ON prompt_library(category);
CREATE INDEX IF NOT EXISTS idx_localized_content_product ON localized_content(product_id);
CREATE INDEX IF NOT EXISTS idx_asset_specs_product ON asset_specs(product_id);
CREATE INDEX IF NOT EXISTS idx_event_type ON marketing_event_log(event_type);
