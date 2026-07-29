-- MAHA SALES ENGINE V1 - Autonomous Optimization Engine Database Schema
-- Phase 10 Database Migration

-- Optimization Jobs
CREATE TABLE IF NOT EXISTS optimization_jobs (
    job_id TEXT PRIMARY KEY,
    optimization_id TEXT NOT NULL,
    category TEXT NOT NULL,
    target_metric TEXT NOT NULL,
    current_value REAL NOT NULL,
    expected_value REAL NOT NULL,
    mode TEXT NOT NULL,
    status TEXT NOT NULL,
    confidence REAL NOT NULL,
    risk_score REAL NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    completed_at TEXT,
    executed_by TEXT,
    metadata TEXT
);

-- Optimization Rules
CREATE TABLE IF NOT EXISTS optimization_rules (
    rule_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    rule_type TEXT NOT NULL,
    category TEXT NOT NULL,
    target_metric TEXT NOT NULL,
    condition TEXT NOT NULL,
    action TEXT NOT NULL,
    priority INTEGER NOT NULL,
    status TEXT NOT NULL,
    cooldown_minutes INTEGER NOT NULL,
    last_triggered_at TEXT,
    trigger_count INTEGER DEFAULT 0,
    created_at TEXT NOT NULL
);

-- Optimization Results
CREATE TABLE IF NOT EXISTS optimization_results (
    result_id TEXT PRIMARY KEY,
    optimization_id TEXT NOT NULL,
    category TEXT NOT NULL,
    result_type TEXT NOT NULL,
    data TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    executed_at TEXT,
    metadata TEXT
);

-- Recommendations
CREATE TABLE IF NOT EXISTS recommendations (
    recommendation_id TEXT PRIMARY KEY,
    optimization_id TEXT NOT NULL,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    evidence TEXT NOT NULL,
    expected_impact TEXT NOT NULL,
    confidence REAL NOT NULL,
    risk_score REAL NOT NULL,
    mode TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    reviewed_by TEXT,
    reviewed_at TEXT,
    metadata TEXT
);

-- Decision History
CREATE TABLE IF NOT EXISTS decision_history (
    decision_id TEXT PRIMARY KEY,
    optimization_id TEXT NOT NULL,
    reason TEXT NOT NULL,
    evidence TEXT NOT NULL,
    confidence REAL NOT NULL,
    risk_score REAL NOT NULL,
    expected_impact TEXT NOT NULL,
    rollback_plan TEXT NOT NULL,
    related_metrics TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    decided_at TEXT,
    decided_by TEXT,
    metadata TEXT
);

-- Simulation Results
CREATE TABLE IF NOT EXISTS simulation_results (
    simulation_id TEXT PRIMARY KEY,
    optimization_id TEXT NOT NULL,
    status TEXT NOT NULL,
    expected_impact TEXT NOT NULL,
    confidence_interval TEXT NOT NULL,
    rollback_plan TEXT NOT NULL,
    related_metrics TEXT NOT NULL,
    executed_at TEXT NOT NULL,
    details TEXT,
    metadata TEXT
);

-- Confidence Scores
CREATE TABLE IF NOT EXISTS confidence_scores (
    score_id TEXT PRIMARY KEY,
    optimization_id TEXT NOT NULL,
    score REAL NOT NULL,
    factors TEXT NOT NULL,
    explanation TEXT NOT NULL,
    calculated_at TEXT NOT NULL,
    metadata TEXT
);

-- Risk Assessments
CREATE TABLE IF NOT EXISTS risk_assessments (
    assessment_id TEXT PRIMARY KEY,
    optimization_id TEXT NOT NULL,
    risk_score REAL NOT NULL,
    risk_breakdown TEXT NOT NULL,
    mitigation_steps TEXT NOT NULL,
    details TEXT NOT NULL,
    assessed_at TEXT NOT NULL,
    metadata TEXT
);

-- Rollback History
CREATE TABLE IF NOT EXISTS rollback_history (
    rollback_id TEXT PRIMARY KEY,
    optimization_id TEXT NOT NULL,
    reason TEXT NOT NULL,
    before_state TEXT NOT NULL,
    after_state TEXT NOT NULL,
    rollback_steps TEXT NOT NULL,
    verification_checks TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    executed_at TEXT,
    completed_at TEXT,
    metadata TEXT
);

-- Approval Requests
CREATE TABLE IF NOT EXISTS approval_requests (
    request_id TEXT PRIMARY KEY,
    optimization_id TEXT NOT NULL,
    decision_id TEXT NOT NULL,
    requester TEXT NOT NULL,
    approver TEXT,
    status TEXT NOT NULL,
    reason TEXT NOT NULL,
    context TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    created_at TEXT NOT NULL,
    decided_at TEXT,
    metadata TEXT
);

-- Policy Evaluations
CREATE TABLE IF NOT EXISTS policy_evaluations (
    evaluation_id TEXT PRIMARY KEY,
    policy_id TEXT NOT NULL,
    optimization_id TEXT NOT NULL,
    result TEXT NOT NULL,
    reason TEXT NOT NULL,
    details TEXT NOT NULL,
    evaluated_at TEXT NOT NULL,
    metadata TEXT
);

-- Optimization Metrics
CREATE TABLE IF NOT EXISTS optimization_metrics (
    metric_id TEXT PRIMARY KEY,
    optimization_id TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    recorded_at TEXT NOT NULL,
    metadata TEXT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_optimization_jobs_status ON optimization_jobs(status);
CREATE INDEX IF NOT EXISTS idx_optimization_jobs_category ON optimization_jobs(category);
CREATE INDEX IF NOT EXISTS idx_recommendations_status ON recommendations(status);
CREATE INDEX IF NOT EXISTS idx_decision_history_status ON decision_history(status);
CREATE INDEX IF NOT EXISTS idx_approval_requests_status ON approval_requests(status);
CREATE INDEX IF NOT EXISTS idx_rollback_history_optimization ON rollback_history(optimization_id);
