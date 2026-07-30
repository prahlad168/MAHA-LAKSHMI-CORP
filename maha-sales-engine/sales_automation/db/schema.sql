-- MAHA SALES ENGINE V1 - Sales Automation Database Schema
-- SQLite Database

-- Automation workflows table
CREATE TABLE IF NOT EXISTS automation_workflows (
    workflow_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    version TEXT NOT NULL,
    nodes TEXT NOT NULL,
    entry_node TEXT NOT NULL,
    exit_node TEXT NOT NULL,
    metadata TEXT,
    created_at TEXT,
    updated_at TEXT
);

-- Workflow versions table
CREATE TABLE IF NOT EXISTS workflow_versions (
    id TEXT PRIMARY KEY,
    workflow_id TEXT NOT NULL,
    version TEXT NOT NULL,
    nodes TEXT NOT NULL,
    changelog TEXT,
    created_at TEXT,
    created_by TEXT,
    FOREIGN KEY (workflow_id) REFERENCES automation_workflows (workflow_id)
);

-- Workflow steps table
CREATE TABLE IF NOT EXISTS workflow_steps (
    id TEXT PRIMARY KEY,
    workflow_id TEXT NOT NULL,
    execution_id TEXT,
    step_name TEXT NOT NULL,
    step_type TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    input_data TEXT,
    output_data TEXT,
    error_message TEXT,
    started_at TEXT,
    completed_at TEXT,
    created_at TEXT,
    FOREIGN KEY (workflow_id) REFERENCES automation_workflows (workflow_id)
);

-- Workflow executions table
CREATE TABLE IF NOT EXISTS workflow_executions (
    execution_id TEXT PRIMARY KEY,
    workflow_id TEXT NOT NULL,
    status TEXT DEFAULT 'running',
    current_node TEXT,
    context TEXT,
    started_at TEXT,
    completed_at TEXT,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TEXT,
    FOREIGN KEY (workflow_id) REFERENCES automation_workflows (workflow_id)
);

-- Workflow history table
CREATE TABLE IF NOT EXISTS workflow_history (
    id TEXT PRIMARY KEY,
    workflow_id TEXT NOT NULL,
    execution_id TEXT NOT NULL,
    action TEXT NOT NULL,
    from_status TEXT,
    to_status TEXT,
    actor TEXT,
    metadata TEXT,
    created_at TEXT,
    FOREIGN KEY (workflow_id) REFERENCES automation_workflows (workflow_id)
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
    max_retries INTEGER DEFAULT 3
);

-- Publication queue table
CREATE TABLE IF NOT EXISTS publication_queue (
    id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,
    marketplace_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    priority TEXT DEFAULT 'normal',
    state TEXT DEFAULT 'queued',
    scheduled_at TEXT,
    created_at TEXT
);

-- Dead letter queue table
CREATE TABLE IF NOT EXISTS dead_letter_queue (
    id TEXT PRIMARY KEY,
    job_type TEXT NOT NULL,
    priority INTEGER DEFAULT 1,
    payload TEXT NOT NULL,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TEXT
);

-- Retry history table
CREATE TABLE IF NOT EXISTS retry_history (
    id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,
    operation TEXT NOT NULL,
    attempt INTEGER NOT NULL,
    error_message TEXT,
    delay_ms INTEGER,
    success BOOLEAN DEFAULT 0,
    created_at TEXT
);

-- Campaigns table
CREATE TABLE IF NOT EXISTS campaigns (
    campaign_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    campaign_type TEXT NOT NULL,
    status TEXT DEFAULT 'draft',
    product_ids TEXT NOT NULL,
    marketplace_ids TEXT NOT NULL,
    schedule TEXT,
    metadata TEXT,
    created_at TEXT,
    updated_at TEXT
);

-- Campaign products table
CREATE TABLE IF NOT EXISTS campaign_products (
    id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    marketplace_id TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    scheduled_at TEXT,
    published_at TEXT,
    created_at TEXT,
    FOREIGN KEY (campaign_id) REFERENCES campaigns (campaign_id)
);

-- Publication schedule table
CREATE TABLE IF NOT EXISTS publication_schedule (
    id TEXT PRIMARY KEY,
    marketplace_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    scheduled_at TEXT NOT NULL,
    action TEXT NOT NULL,
    status TEXT DEFAULT 'scheduled',
    metadata TEXT,
    created_at TEXT
);

-- Publication events table
CREATE TABLE IF NOT EXISTS publication_events (
    id TEXT PRIMARY KEY,
    marketplace_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    data TEXT,
    source TEXT DEFAULT 'system',
    created_at TEXT
);

-- Publication status table
CREATE TABLE IF NOT EXISTS publication_status (
    id TEXT PRIMARY KEY,
    marketplace_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    status TEXT NOT NULL,
    details TEXT,
    updated_at TEXT
);

-- Sync history table
CREATE TABLE IF NOT EXISTS sync_history (
    id TEXT PRIMARY KEY,
    marketplace_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    sync_type TEXT NOT NULL,
    fields TEXT,
    result TEXT,
    success BOOLEAN DEFAULT 1,
    duration_ms INTEGER,
    created_at TEXT
);

-- Approval requests table
CREATE TABLE IF NOT EXISTS approval_requests (
    request_id TEXT PRIMARY KEY,
    workflow_id TEXT,
    execution_id TEXT,
    marketplace_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    approval_type TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    requested_by TEXT DEFAULT 'system',
    approved_by TEXT,
    feedback TEXT,
    requested_at TEXT,
    responded_at TEXT,
    expires_at TEXT,
    metadata TEXT
);

-- Approval history table
CREATE TABLE IF NOT EXISTS approval_history (
    id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL,
    action TEXT NOT NULL,
    actor TEXT NOT NULL,
    feedback TEXT,
    created_at TEXT,
    FOREIGN KEY (request_id) REFERENCES approval_requests (request_id)
);

-- Rules table
CREATE TABLE IF NOT EXISTS rules (
    rule_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    condition TEXT NOT NULL,
    action TEXT NOT NULL,
    priority INTEGER DEFAULT 100,
    enabled BOOLEAN DEFAULT 1,
    created_at TEXT
);

-- Policies table
CREATE TABLE IF NOT EXISTS policies (
    policy_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    policy_type TEXT NOT NULL,
    description TEXT,
    rules TEXT NOT NULL,
    enabled BOOLEAN DEFAULT 1,
    created_at TEXT,
    updated_at TEXT
);

-- Notification log table
CREATE TABLE IF NOT EXISTS notification_log (
    id TEXT PRIMARY KEY,
    channel TEXT NOT NULL,
    recipient TEXT NOT NULL,
    subject TEXT,
    body TEXT,
    severity TEXT DEFAULT 'info',
    metadata TEXT,
    sent_at TEXT,
    status TEXT DEFAULT 'pending',
    created_at TEXT
);

-- Automation metrics table
CREATE TABLE IF NOT EXISTS automation_metrics (
    id TEXT PRIMARY KEY,
    metric_name TEXT NOT NULL,
    metric_type TEXT NOT NULL,
    value TEXT NOT NULL,
    tags TEXT,
    created_at TEXT
);

-- Automation health table
CREATE TABLE IF NOT EXISTS automation_health (
    id TEXT PRIMARY KEY,
    component_name TEXT NOT NULL,
    status TEXT NOT NULL,
    uptime INTEGER DEFAULT 0,
    last_check TEXT,
    error_message TEXT,
    metrics TEXT,
    created_at TEXT
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

-- Audit log table
CREATE TABLE IF NOT EXISTS audit_log (
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

-- Indexes
CREATE INDEX IF NOT EXISTS idx_workflows_status ON automation_workflows(version);
CREATE INDEX IF NOT EXISTS idx_executions_workflow ON workflow_executions(workflow_id);
CREATE INDEX IF NOT EXISTS idx_executions_status ON workflow_executions(status);
CREATE INDEX IF NOT EXISTS idx_publication_jobs_marketplace ON publication_jobs(marketplace_id);
CREATE INDEX IF NOT EXISTS idx_publication_jobs_status ON publication_jobs(status);
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);
CREATE INDEX IF NOT EXISTS idx_approval_requests_status ON approval_requests(status);
CREATE INDEX IF NOT EXISTS idx_audit_log_resource ON audit_log(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_created ON audit_log(created_at);
CREATE INDEX IF NOT EXISTS idx_notification_log_channel ON notification_log(channel);
CREATE INDEX IF NOT EXISTS idx_webhook_logs_marketplace ON webhook_logs(marketplace_id);
