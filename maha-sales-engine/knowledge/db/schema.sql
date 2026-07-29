-- MAHA SALES ENGINE V1 - Knowledge & Learning Platform Database Schema
-- Phase 11 Database Migration

-- Knowledge Items
CREATE TABLE IF NOT EXISTS knowledge_items (
    knowledge_id TEXT PRIMARY KEY,
    knowledge_type TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source TEXT NOT NULL,
    version INTEGER NOT NULL,
    confidence REAL NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata TEXT
);

-- Knowledge Versions
CREATE TABLE IF NOT EXISTS knowledge_versions (
    version_id TEXT PRIMARY KEY,
    knowledge_id TEXT NOT NULL,
    version INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    author TEXT NOT NULL,
    change_reason TEXT NOT NULL,
    created_at TEXT NOT NULL,
    metadata TEXT
);

-- Knowledge Sources
CREATE TABLE IF NOT EXISTS knowledge_sources (
    source_id TEXT PRIMARY KEY,
    source_name TEXT NOT NULL,
    source_type TEXT NOT NULL,
    description TEXT,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
);

-- Decision Memory
CREATE TABLE IF NOT EXISTS decision_memory (
    memory_id TEXT PRIMARY KEY,
    decision_id TEXT NOT NULL,
    optimization_id TEXT NOT NULL,
    category TEXT NOT NULL,
    decision TEXT NOT NULL,
    reason TEXT NOT NULL,
    evidence TEXT NOT NULL,
    confidence REAL NOT NULL,
    risk_score REAL NOT NULL,
    outcome TEXT NOT NULL,
    reward REAL NOT NULL,
    created_at TEXT NOT NULL
);

-- Experiment Memory
CREATE TABLE IF NOT EXISTS experiment_memory (
    memory_id TEXT PRIMARY KEY,
    experiment_id TEXT NOT NULL,
    optimization_id TEXT NOT NULL,
    experiment_type TEXT NOT NULL,
    config TEXT NOT NULL,
    results TEXT NOT NULL,
    success INTEGER NOT NULL,
    reward REAL NOT NULL,
    created_at TEXT NOT NULL
);

-- Pattern Library
CREATE TABLE IF NOT EXISTS pattern_library (
    pattern_id TEXT PRIMARY KEY,
    pattern_type TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    confidence REAL NOT NULL,
    data_points INTEGER NOT NULL,
    evidence TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Knowledge Graph Nodes
CREATE TABLE IF NOT EXISTS knowledge_graph_nodes (
    node_id TEXT PRIMARY KEY,
    node_type TEXT NOT NULL,
    label TEXT NOT NULL,
    properties TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- Knowledge Graph Edges
CREATE TABLE IF NOT EXISTS knowledge_graph_edges (
    edge_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    edge_type TEXT NOT NULL,
    properties TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- Learning Events
CREATE TABLE IF NOT EXISTS learning_events (
    event_id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    source TEXT NOT NULL,
    data TEXT NOT NULL,
    outcome TEXT NOT NULL,
    reward REAL NOT NULL,
    context TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- Semantic Embeddings
CREATE TABLE IF NOT EXISTS semantic_embeddings (
    embedding_id TEXT PRIMARY KEY,
    knowledge_id TEXT NOT NULL,
    embedding TEXT NOT NULL,
    dimension INTEGER NOT NULL,
    created_at TEXT NOT NULL
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_knowledge_items_type ON knowledge_items(knowledge_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_items_source ON knowledge_items(source);
CREATE INDEX IF NOT EXISTS idx_decision_memory_category ON decision_memory(category);
CREATE INDEX IF NOT EXISTS idx_experiment_memory_type ON experiment_memory(experiment_type);
CREATE INDEX IF NOT EXISTS idx_pattern_library_type ON pattern_library(pattern_type);
CREATE INDEX IF NOT EXISTS idx_learning_events_type ON learning_events(event_type);
