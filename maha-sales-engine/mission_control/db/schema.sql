-- MAHA Sales Engine V1 - Mission Control Database Schema
-- SQLite Database

-- Missions table
CREATE TABLE IF NOT EXISTS missions (
    mission_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    config TEXT NOT NULL,
    result TEXT
);

-- Mission metrics table
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

-- Mission alerts table
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

-- Mission audit table
CREATE TABLE IF NOT EXISTS mission_audit (
    audit_id TEXT PRIMARY KEY,
    mission_id TEXT NOT NULL,
    action TEXT NOT NULL,
    user_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    details TEXT,
    FOREIGN KEY (mission_id) REFERENCES missions (mission_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_missions_status ON missions(status);
CREATE INDEX IF NOT EXISTS idx_missions_created ON missions(created_at);
CREATE INDEX IF NOT EXISTS idx_metrics_mission ON mission_metrics(mission_id);
CREATE INDEX IF NOT EXISTS idx_alerts_mission ON mission_alerts(mission_id);
CREATE INDEX IF NOT EXISTS idx_audit_mission ON mission_audit(mission_id);
