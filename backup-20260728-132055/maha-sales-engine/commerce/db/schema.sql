-- MAHA SALES ENGINE V1 - Commerce Database Schema
-- SQLite Database

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    language TEXT DEFAULT 'en',
    currency TEXT DEFAULT 'USD',
    billing_profile TEXT,
    purchase_history TEXT,
    subscription_history TEXT,
    license_history TEXT,
    download_history TEXT,
    created_at TEXT,
    updated_at TEXT
);

-- Organizations table
CREATE TABLE IF NOT EXISTS organizations (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    owner_customer_id TEXT NOT NULL,
    members TEXT,
    billing_profile TEXT,
    created_at TEXT,
    updated_at TEXT
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    items TEXT NOT NULL,
    total_amount REAL NOT NULL,
    currency TEXT NOT NULL,
    status TEXT DEFAULT 'draft',
    payment_method TEXT,
    payment_transaction_id TEXT,
    metadata TEXT,
    created_at TEXT,
    updated_at TEXT
);

-- Order items table
CREATE TABLE IF NOT EXISTS order_items (
    id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    product_name TEXT,
    quantity INTEGER DEFAULT 1,
    unit_price REAL NOT NULL,
    total_price REAL NOT NULL,
    metadata TEXT,
    FOREIGN KEY (order_id) REFERENCES orders (order_id)
);

-- Shopping carts table
CREATE TABLE IF NOT EXISTS shopping_carts (
    id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    items TEXT NOT NULL,
    created_at TEXT,
    updated_at TEXT
);

-- Payment methods table
CREATE TABLE IF NOT EXISTS payment_methods (
    id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    method_type TEXT NOT NULL,
    last_four TEXT,
    expiry_month INTEGER,
    expiry_year INTEGER,
    is_default BOOLEAN DEFAULT 0,
    metadata TEXT,
    created_at TEXT
);

-- Payment transactions table
CREATE TABLE IF NOT EXISTS payment_transactions (
    id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    provider_transaction_id TEXT,
    amount REAL NOT NULL,
    currency TEXT NOT NULL,
    status TEXT NOT NULL,
    payment_method TEXT,
    metadata TEXT,
    created_at TEXT
);

-- Payment providers table
CREATE TABLE IF NOT EXISTS payment_providers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    enabled BOOLEAN DEFAULT 1,
    config TEXT,
    credentials TEXT,
    priority INTEGER DEFAULT 0,
    created_at TEXT,
    updated_at TEXT
);

-- Payment attempts table
CREATE TABLE IF NOT EXISTS payment_attempts (
    id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    attempt_number INTEGER DEFAULT 1,
    status TEXT NOT NULL,
    error_message TEXT,
    metadata TEXT,
    created_at TEXT
);

-- Licenses table
CREATE TABLE IF NOT EXISTS licenses (
    license_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    order_id TEXT NOT NULL,
    license_type TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    key TEXT NOT NULL UNIQUE,
    activated_at TEXT,
    expires_at TEXT,
    activations INTEGER DEFAULT 0,
    max_activations INTEGER DEFAULT 1,
    metadata TEXT,
    created_at TEXT
);

-- License activations table
CREATE TABLE IF NOT EXISTS license_activations (
    id TEXT PRIMARY KEY,
    license_id TEXT NOT NULL,
    activation_data TEXT,
    ip_address TEXT,
    user_agent TEXT,
    activated_at TEXT,
    FOREIGN KEY (license_id) REFERENCES licenses (license_id)
);

-- Subscriptions table
CREATE TABLE IF NOT EXISTS subscriptions (
    id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    plan_id TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    current_period_start TEXT,
    current_period_end TEXT,
    cancel_at_period_end BOOLEAN DEFAULT 0,
    trial_end TEXT,
    metadata TEXT,
    created_at TEXT,
    updated_at TEXT
);

-- Subscription events table
CREATE TABLE IF NOT EXISTS subscription_events (
    id TEXT PRIMARY KEY,
    subscription_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    data TEXT,
    created_at TEXT,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions (id)
);

-- Deliveries table
CREATE TABLE IF NOT EXISTS deliveries (
    delivery_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    file_path TEXT NOT NULL,
    download_token TEXT NOT NULL UNIQUE,
    download_url TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    download_count INTEGER DEFAULT 0,
    max_downloads INTEGER DEFAULT 5,
    created_at TEXT
);

-- Download logs table
CREATE TABLE IF NOT EXISTS download_logs (
    download_id TEXT PRIMARY KEY,
    delivery_id TEXT NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    downloaded_at TEXT
);

-- Invoices table
CREATE TABLE IF NOT EXISTS invoices (
    id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    invoice_number TEXT NOT NULL UNIQUE,
    amount REAL NOT NULL,
    currency TEXT NOT NULL,
    tax_amount REAL DEFAULT 0,
    total_amount REAL NOT NULL,
    status TEXT DEFAULT 'draft',
    pdf_path TEXT,
    metadata TEXT,
    created_at TEXT
);

-- Receipts table
CREATE TABLE IF NOT EXISTS receipts (
    id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    receipt_number TEXT NOT NULL UNIQUE,
    amount REAL NOT NULL,
    currency TEXT NOT NULL,
    payment_method TEXT,
    pdf_path TEXT,
    metadata TEXT,
    created_at TEXT
);

-- Coupons table
CREATE TABLE IF NOT EXISTS coupons (
    id TEXT PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    discount_type TEXT NOT NULL,
    discount_value REAL NOT NULL,
    currency TEXT,
    min_purchase REAL DEFAULT 0,
    max_discount REAL,
    usage_limit INTEGER,
    used_count INTEGER DEFAULT 0,
    customer_specific BOOLEAN DEFAULT 0,
    customer_ids TEXT,
    product_ids TEXT,
    start_date TEXT,
    end_date TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TEXT
);

-- Promotions table
CREATE TABLE IF NOT EXISTS promotions (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    promotion_type TEXT NOT NULL,
    discount_type TEXT NOT NULL,
    discount_value REAL NOT NULL,
    currency TEXT,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    priority INTEGER DEFAULT 0,
    eligibility_rules TEXT,
    metadata TEXT,
    created_at TEXT,
    updated_at TEXT
);

-- Promotion rules table
CREATE TABLE IF NOT EXISTS promotion_rules (
    id TEXT PRIMARY KEY,
    promotion_id TEXT NOT NULL,
    rule_type TEXT NOT NULL,
    conditions TEXT NOT NULL,
    actions TEXT NOT NULL,
    priority INTEGER DEFAULT 0,
    created_at TEXT,
    FOREIGN KEY (promotion_id) REFERENCES promotions (id)
);

-- Refunds table
CREATE TABLE IF NOT EXISTS refunds (
    id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    payment_transaction_id TEXT NOT NULL,
    amount REAL NOT NULL,
    currency TEXT NOT NULL,
    reason TEXT,
    status TEXT DEFAULT 'pending',
    provider_refund_id TEXT,
    metadata TEXT,
    created_at TEXT,
    updated_at TEXT
);

-- Wallets table
CREATE TABLE IF NOT EXISTS wallets (
    id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    balance REAL DEFAULT 0,
    currency TEXT NOT NULL,
    created_at TEXT,
    updated_at TEXT
);

-- Wallet transactions table
CREATE TABLE IF NOT EXISTS wallet_transactions (
    id TEXT PRIMARY KEY,
    wallet_id TEXT NOT NULL,
    transaction_type TEXT NOT NULL,
    amount REAL NOT NULL,
    currency TEXT NOT NULL,
    reference_id TEXT,
    description TEXT,
    created_at TEXT,
    FOREIGN KEY (wallet_id) REFERENCES wallets (id)
);

-- Payouts table
CREATE TABLE IF NOT EXISTS payouts (
    id TEXT PRIMARY KEY,
    recipient_id TEXT NOT NULL,
    recipient_type TEXT NOT NULL,
    amount REAL NOT NULL,
    currency TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    payout_method TEXT,
    provider_payout_id TEXT,
    metadata TEXT,
    created_at TEXT,
    updated_at TEXT
);

-- Tax rules table
CREATE TABLE IF NOT EXISTS tax_rules (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    tax_type TEXT NOT NULL,
    rate REAL NOT NULL,
    country TEXT,
    state TEXT,
    product_type TEXT,
    priority INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    created_at TEXT
);

-- Fraud events table
CREATE TABLE IF NOT EXISTS fraud_events (
    id TEXT PRIMARY KEY,
    order_id TEXT,
    customer_id TEXT,
    event_type TEXT NOT NULL,
    risk_score REAL,
    details TEXT,
    action_taken TEXT,
    created_at TEXT
);

-- Commerce events table
CREATE TABLE IF NOT EXISTS commerce_events (
    id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    source TEXT DEFAULT 'commerce',
    event_id TEXT NOT NULL,
    data TEXT NOT NULL,
    created_at TEXT
);

-- Audit log table
CREATE TABLE IF NOT EXISTS commerce_audit_log (
    id TEXT PRIMARY KEY,
    action TEXT NOT NULL,
    actor TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    before_data TEXT,
    after_data TEXT,
    ip_address TEXT,
    result TEXT DEFAULT 'success',
    metadata TEXT,
    created_at TEXT
);

-- Commerce metrics table
CREATE TABLE IF NOT EXISTS commerce_metrics (
    id TEXT PRIMARY KEY,
    metric_name TEXT NOT NULL,
    metric_type TEXT NOT NULL,
    value TEXT NOT NULL,
    tags TEXT,
    created_at TEXT
);

-- Commerce health table
CREATE TABLE IF NOT EXISTS commerce_health (
    id TEXT PRIMARY KEY,
    component_name TEXT NOT NULL,
    status TEXT NOT NULL,
    uptime INTEGER DEFAULT 0,
    last_check TEXT,
    error_message TEXT,
    metrics TEXT,
    created_at TEXT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_licenses_customer ON licenses(customer_id);
CREATE INDEX IF NOT EXISTS idx_licenses_product ON licenses(product_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_customer ON subscriptions(customer_id);
CREATE INDEX IF NOT EXISTS idx_deliveries_order ON deliveries(order_id);
CREATE INDEX IF NOT EXISTS idx_invoices_customer ON invoices(customer_id);
CREATE INDEX IF NOT EXISTS idx_refunds_order ON refunds(order_id);
CREATE INDEX IF NOT EXISTS idx_wallets_customer ON wallets(customer_id);
CREATE INDEX IF NOT EXISTS idx_payouts_recipient ON payouts(recipient_id);
CREATE INDEX IF NOT EXISTS idx_fraud_events_order ON fraud_events(order_id);
CREATE INDEX IF NOT EXISTS idx_commerce_events_type ON commerce_events(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_log_resource ON commerce_audit_log(resource_type, resource_id);
