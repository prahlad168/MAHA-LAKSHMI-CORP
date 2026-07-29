-- MAHA LAKSHMI CORP - Revenue Sprint 2 Database Migration
-- Payment & Accounting Foundation

-- Marketplace sales table
CREATE TABLE IF NOT EXISTS marketplace_sales (
    id TEXT PRIMARY KEY,
    gumroad_purchase_id TEXT UNIQUE NOT NULL,
    product_id TEXT NOT NULL,
    marketplace_product_id TEXT NOT NULL,
    account_id TEXT NOT NULL,
    customer_email TEXT,
    customer_name TEXT,
    amount REAL NOT NULL,
    currency TEXT NOT NULL DEFAULT 'USD',
    tax REAL DEFAULT 0,
    fee REAL DEFAULT 0,
    net_amount REAL NOT NULL,
    payment_method TEXT,
    payment_status TEXT NOT NULL DEFAULT 'pending',
    license_key TEXT,
    download_count INTEGER DEFAULT 0,
    refunded INTEGER DEFAULT 0,
    refund_amount REAL DEFAULT 0,
    chargeback INTEGER DEFAULT 0,
    sale_date TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- Revenue records table for daily aggregation
CREATE TABLE IF NOT EXISTS revenue_records (
    id TEXT PRIMARY KEY,
    date TEXT NOT NULL,
    marketplace TEXT NOT NULL,
    product_id TEXT,
    product_name TEXT,
    category TEXT,
    sales_count INTEGER NOT NULL DEFAULT 0,
    gross_amount REAL NOT NULL DEFAULT 0,
    fee_amount REAL NOT NULL DEFAULT 0,
    tax_amount REAL NOT NULL DEFAULT 0,
    net_amount REAL NOT NULL DEFAULT 0,
    refund_count INTEGER DEFAULT 0,
    refund_amount REAL DEFAULT 0,
    chargeback_count INTEGER DEFAULT 0,
    chargeback_amount REAL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Accounting entries table for double-entry bookkeeping
CREATE TABLE IF NOT EXISTS accounting_entries (
    id TEXT PRIMARY KEY,
    entry_date TEXT NOT NULL,
    account_code TEXT NOT NULL,
    account_name TEXT NOT NULL,
    entry_type TEXT NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    currency TEXT NOT NULL DEFAULT 'USD',
    description TEXT,
    reference_type TEXT,
    reference_id TEXT,
    related_entry_id TEXT,
    created_at TEXT NOT NULL
);

-- Payouts table
CREATE TABLE IF NOT EXISTS payouts (
    id TEXT PRIMARY KEY,
    marketplace TEXT NOT NULL,
    payout_id TEXT UNIQUE NOT NULL,
    amount REAL NOT NULL,
    currency TEXT NOT NULL DEFAULT 'USD',
    fee REAL DEFAULT 0,
    tax REAL DEFAULT 0,
    net_amount REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    payout_date TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_marketplace_sales_product_id ON marketplace_sales(product_id);
CREATE INDEX IF NOT EXISTS idx_marketplace_sales_account_id ON marketplace_sales(account_id);
CREATE INDEX IF NOT EXISTS idx_marketplace_sales_sale_date ON marketplace_sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_marketplace_sales_gumroad_purchase_id ON marketplace_sales(gumroad_purchase_id);
CREATE INDEX IF NOT EXISTS idx_revenue_records_date ON revenue_records(date);
CREATE INDEX IF NOT EXISTS idx_revenue_records_marketplace ON revenue_records(marketplace);
CREATE INDEX IF NOT EXISTS idx_accounting_entries_date ON accounting_entries(entry_date);
CREATE INDEX IF NOT EXISTS idx_accounting_entries_account_code ON accounting_entries(account_code);
CREATE INDEX IF NOT EXISTS idx_payouts_marketplace ON payouts(marketplace);
CREATE INDEX IF NOT EXISTS idx_payouts_status ON payouts(status);
