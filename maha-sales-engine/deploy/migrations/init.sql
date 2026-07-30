-- MAHA Sales Engine V1 - Production Database Initialization
-- PostgreSQL initialization script

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create application user if not exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'maha_app') THEN
        CREATE ROLE maha_app WITH LOGIN PASSWORD 'maha_app_password';
    END IF;
END
$$;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE maha_sales TO maha;
GRANT ALL ON SCHEMA public TO maha;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO maha;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO maha;

-- Create mission control tables if not exists
CREATE TABLE IF NOT EXISTS missions (
    mission_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    config TEXT NOT NULL,
    result TEXT
);

CREATE TABLE IF NOT EXISTS mission_metrics (
    metric_id TEXT PRIMARY KEY,
    mission_id TEXT NOT NULL,
    name TEXT NOT NULL,
    value REAL NOT NULL,
    unit TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    tags TEXT,
    FOREIGN KEY (mission_id) REFERENCES missions (mission_id)
);

CREATE TABLE IF NOT EXISTS mission_alerts (
    alert_id TEXT PRIMARY KEY,
    mission_id TEXT NOT NULL,
    severity TEXT NOT NULL,
    message TEXT NOT NULL,
    source TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    acknowledged INTEGER DEFAULT 0,
    metadata TEXT,
    FOREIGN KEY (mission_id) REFERENCES missions (mission_id)
);

CREATE TABLE IF NOT EXISTS mission_audit (
    audit_id TEXT PRIMARY KEY,
    mission_id TEXT NOT NULL,
    action TEXT NOT NULL,
    user_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    details TEXT,
    FOREIGN KEY (mission_id) REFERENCES missions (mission_id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_missions_status ON missions(status);
CREATE INDEX IF NOT EXISTS idx_missions_created ON missions(created_at);
CREATE INDEX IF NOT EXISTS idx_metrics_mission ON mission_metrics(mission_id);
CREATE INDEX IF NOT EXISTS idx_alerts_mission ON mission_alerts(mission_id);
CREATE INDEX IF NOT EXISTS idx_audit_mission ON mission_audit(mission_id);

-- Insert initial data
INSERT INTO missions (mission_id, name, status, created_at, updated_at, config, result)
VALUES ('system-init', 'System Initialization', 'completed', NOW(), NOW(), '{}', '{}')
ON CONFLICT (mission_id) DO NOTHING;
