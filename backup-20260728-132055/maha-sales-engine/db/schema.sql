-- MAHA SALES ENGINE V1 - Database Schema
-- SQLite Database

-- Products table
CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    price_usd REAL,
    price_idr REAL,
    category TEXT,
    features TEXT,
    status TEXT DEFAULT 'active',
    created_at TEXT,
    updated_at TEXT
);

-- Leads table
CREATE TABLE IF NOT EXISTS leads (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    company TEXT,
    industry TEXT,
    country TEXT,
    language TEXT,
    source TEXT,
    status TEXT DEFAULT 'new',
    score INTEGER DEFAULT 0,
    created_at TEXT,
    last_contact TEXT,
    followup_count INTEGER DEFAULT 0,
    notes TEXT
);

-- Outreach log table
CREATE TABLE IF NOT EXISTS outreach_log (
    id TEXT PRIMARY KEY,
    lead_id TEXT,
    channel TEXT NOT NULL,
    template_type TEXT,
    content TEXT,
    status TEXT DEFAULT 'sent',
    sent_at TEXT,
    response_received INTEGER DEFAULT 0,
    response_at TEXT,
    FOREIGN KEY (lead_id) REFERENCES leads (id)
);

-- Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id TEXT PRIMARY KEY,
    gateway TEXT NOT NULL,
    customer_email TEXT,
    customer_name TEXT,
    amount REAL NOT NULL,
    currency TEXT NOT NULL,
    fee_amount REAL DEFAULT 0.0,
    net_amount REAL NOT NULL,
    product_id TEXT,
    status TEXT DEFAULT 'pending',
    payment_method TEXT,
    created_at TEXT,
    completed_at TEXT,
    metadata TEXT
);

-- Reports table
CREATE TABLE IF NOT EXISTS reports (
    id TEXT PRIMARY KEY,
    report_type TEXT NOT NULL,
    date TEXT NOT NULL,
    data TEXT NOT NULL,
    created_at TEXT
);

-- System metrics table
CREATE TABLE IF NOT EXISTS system_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    cpu_usage REAL,
    memory_usage REAL,
    disk_usage REAL,
    active_leads INTEGER,
    queue_size INTEGER
);

-- Marketplace listings table
CREATE TABLE IF NOT EXISTS marketplace_listings (
    id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    marketplace TEXT NOT NULL,
    status TEXT DEFAULT 'draft',
    url TEXT,
    price REAL,
    currency TEXT DEFAULT 'USD',
    views INTEGER DEFAULT 0,
    sales INTEGER DEFAULT 0,
    reviews INTEGER DEFAULT 0,
    rating REAL DEFAULT 0.0,
    last_synced TEXT,
    created_at TEXT,
    FOREIGN KEY (product_id) REFERENCES products (id)
);

-- Content templates table
CREATE TABLE IF NOT EXISTS content_templates (
    id TEXT PRIMARY KEY,
    template_type TEXT NOT NULL,
    language TEXT NOT NULL,
    subject TEXT,
    body TEXT,
    variables TEXT,
    performance_score REAL DEFAULT 0.0,
    usage_count INTEGER DEFAULT 0,
    created_at TEXT
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_country ON leads(country);
CREATE INDEX IF NOT EXISTS idx_leads_created ON leads(created_at);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(created_at);
CREATE INDEX IF NOT EXISTS idx_transactions_product ON transactions(product_id);
CREATE INDEX IF NOT EXISTS idx_reports_date ON reports(date);
CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON system_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_listings_product ON marketplace_listings(product_id);
CREATE INDEX IF NOT EXISTS idx_listings_marketplace ON marketplace_listings(marketplace);
CREATE INDEX IF NOT EXISTS idx_outreach_lead ON outreach_log(lead_id);
CREATE INDEX IF NOT EXISTS idx_outreach_channel ON outreach_log(channel);
CREATE INDEX IF NOT EXISTS idx_outreach_sent ON outreach_log(sent_at);
