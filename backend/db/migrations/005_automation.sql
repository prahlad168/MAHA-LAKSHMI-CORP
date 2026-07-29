-- Migration 005: Automation and optimization tables
CREATE TABLE IF NOT EXISTS automation_workflows (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    trigger_type TEXT NOT NULL,
    actions TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    last_run TEXT,
    run_count INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS optimizations (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    target_metric TEXT NOT NULL,
    current_value REAL,
    proposed_value REAL,
    expected_improvement REAL,
    status TEXT NOT NULL DEFAULT 'pending',
    executed_at TEXT,
    result TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ai_workers (
    id TEXT PRIMARY KEY,
    worker_id TEXT UNIQUE NOT NULL,
    type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'idle',
    last_heartbeat TEXT,
    tasks_processed INTEGER DEFAULT 0,
    metadata TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS product_generation_jobs (
    id TEXT PRIMARY KEY,
    product_data TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    worker_id TEXT,
    result TEXT,
    error TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_workflows_status ON automation_workflows(status);
CREATE INDEX IF NOT EXISTS idx_optimizations_status ON optimizations(status);
CREATE INDEX IF NOT EXISTS idx_workers_status ON ai_workers(status);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON product_generation_jobs(status);
