#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Knowledge API Routes
REST API for Knowledge & Learning Platform.
"""

import os
import sys
import json
import time
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel, Field

logger = logging.getLogger("maha-sales-engine.knowledge.api")


# Pydantic models
class KnowledgeRequest(BaseModel):
    knowledge_type: str
    title: str
    content: Dict[str, Any]
    source: str
    author: str = "system"


class SearchRequest(BaseModel):
    query: str
    knowledge_type: Optional[str] = None
    limit: int = 10


# Create FastAPI app
app = FastAPI(
    title="MAHA Sales Engine V1 - Knowledge API",
    description="Knowledge & Learning Platform API",
    version="1.0.0"
)


# Dependency injection
def get_knowledge_core():
    from knowledge.core.knowledge_core import KnowledgeCore
    from knowledge.engines.learning_engine import LearningEngine
    from knowledge.engines.memory_engine import MemoryEngine
    from knowledge.engines.knowledge_graph import KnowledgeGraph
    from knowledge.engines.semantic_search import SemanticSearch
    from knowledge.engines.embedding_service import EmbeddingService
    from knowledge.db.knowledge_db import KnowledgeDatabaseManager
    from knowledge.infrastructure.knowledge_versioning import KnowledgeVersioning
    from knowledge.infrastructure.knowledge_audit import KnowledgeAudit
    from shared.database import DatabaseManager
    
    db = DatabaseManager("data/knowledge.db")
    versioning = KnowledgeVersioning(db)
    audit = KnowledgeAudit(db)
    learning_engine = LearningEngine(db)
    memory_engine = MemoryEngine(db)
    embedding_service = EmbeddingService()
    knowledge_graph = KnowledgeGraph(db)
    semantic_search = SemanticSearch(embedding_service, db)
    core = KnowledgeCore(db, learning_engine, memory_engine, knowledge_graph, semantic_search)
    
    return core


def get_knowledge_repository():
    from knowledge.engines.knowledge_repository import KnowledgeRepository
    from knowledge.db.knowledge_db import KnowledgeDatabaseManager
    from knowledge.infrastructure.knowledge_versioning import KnowledgeVersioning
    from knowledge.infrastructure.knowledge_audit import KnowledgeAudit
    from shared.database import DatabaseManager
    
    db = DatabaseManager("data/knowledge.db")
    versioning = KnowledgeVersioning(db)
    audit = KnowledgeAudit(db)
    return KnowledgeRepository(db, versioning, audit)


def get_learning_engine():
    from knowledge.engines.learning_engine import LearningEngine
    from knowledge.db.knowledge_db import KnowledgeDatabaseManager
    from shared.database import DatabaseManager
    
    db = DatabaseManager("data/knowledge.db")
    return LearningEngine(db)


def get_semantic_search():
    from knowledge.engines.semantic_search import SemanticSearch
    from knowledge.engines.embedding_service import EmbeddingService
    from knowledge.db.knowledge_db import KnowledgeDatabaseManager
    from shared.database import DatabaseManager
    
    db = DatabaseManager("data/knowledge.db")
    embedding_service = EmbeddingService()
    return SemanticSearch(embedding_service, db)


def get_knowledge_graph():
    from knowledge.engines.knowledge_graph import KnowledgeGraph
    from knowledge.db.knowledge_db import KnowledgeDatabaseManager
    from shared.database import DatabaseManager
    
    db = DatabaseManager("data/knowledge.db")
    return KnowledgeGraph(db)


def get_metrics_collector():
    from knowledge.infrastructure.knowledge_metrics import KnowledgeMetricsCollector
    return KnowledgeMetricsCollector()


# API Endpoints

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "knowledge", "version": "1.0.0"}


@app.post("/api/v1/knowledge")
async def create_knowledge(request: KnowledgeRequest, core = Depends(get_knowledge_core)):
    """Store knowledge item"""
    from knowledge.core.knowledge_core import KnowledgeType
    
    knowledge_type = KnowledgeType(request.knowledge_type)
    context = core.create_knowledge(
        knowledge_type=knowledge_type,
        title=request.title,
        content=request.content,
        source=request.source
    )
    
    return {
        "knowledge_id": context.knowledge_id,
        "knowledge_type": context.knowledge_type.value,
        "title": context.title,
        "version": context.version,
        "created_at": context.created_at
    }


@app.get("/api/v1/knowledge")
async def list_knowledge(knowledge_type: Optional[str] = None, core = Depends(get_knowledge_core)):
    """List knowledge items"""
    from knowledge.core.knowledge_core import KnowledgeType
    
    type_filter = KnowledgeType(knowledge_type) if knowledge_type else None
    items = core.list_knowledge(knowledge_type=type_filter)
    
    return {
        "knowledge_items": [
            {
                "knowledge_id": k.knowledge_id,
                "knowledge_type": k.knowledge_type.value,
                "title": k.title,
                "source": k.source,
                "version": k.version,
                "created_at": k.created_at
            }
            for k in items
        ]
    }


@app.get("/api/v1/knowledge/{knowledge_id}")
async def get_knowledge(knowledge_id: str, core = Depends(get_knowledge_core)):
    """Get knowledge item"""
    context = core.get_knowledge(knowledge_id)
    if not context:
        raise HTTPException(status_code=404, detail="Knowledge not found")
    
    return {
        "knowledge_id": context.knowledge_id,
        "knowledge_type": context.knowledge_type.value,
        "title": context.title,
        "content": context.content,
        "source": context.source,
        "version": context.version,
        "created_at": context.created_at,
        "updated_at": context.updated_at
    }


@app.post("/api/v1/knowledge/search")
async def search_knowledge(request: SearchRequest, repo = Depends(get_knowledge_repository)):
    """Search knowledge items"""
    results = repo.search(request.query, knowledge_type=request.knowledge_type)
    
    return {
        "query": request.query,
        "results": [
            {
                "knowledge_id": k.knowledge_id,
                "title": k.title,
                "content": k.content,
                "source": k.source,
                "confidence": k.confidence
            }
            for k in results[:request.limit]
        ]
    }


@app.post("/api/v1/knowledge/semantic-search")
async def semantic_search(request: SearchRequest, search = Depends(get_semantic_search)):
    """Semantic search"""
    results = search.search(request.query, top_k=request.limit)
    
    return {
        "query": request.query,
        "results": [
            {
                "result_id": r.result_id,
                "knowledge_id": r.knowledge_id,
                "score": r.score,
                "snippet": r.snippet
            }
            for r in results
        ]
    }


@app.get("/api/v1/decisions")
async def get_decision_history(category: Optional[str] = None, memory = Depends(get_knowledge_core)):
    """Get decision history"""
    memories = memory.memory_engine._memory.get("decision", {}).values()
    
    if category:
        memories = [m for m in memories if m.metadata.get("category") == category]
    
    return {
        "decisions": [
            {
                "memory_id": m.memory_id,
                "decision_id": m.metadata.get("decision_id"),
                "category": m.metadata.get("category"),
                "decision": m.value.get("decision"),
                "confidence": m.value.get("confidence"),
                "reward": m.value.get("reward")
            }
            for m in memories
        ]
    }


@app.get("/api/v1/experiments")
async def get_experiment_history(experiment_type: Optional[str] = None, memory = Depends(get_knowledge_core)):
    """Get experiment history"""
    memories = memory.memory_engine._memory.get("experiment", {}).values()
    
    if experiment_type:
        memories = [m for m in memories if m.metadata.get("experiment_type") == experiment_type]
    
    return {
        "experiments": [
            {
                "memory_id": m.memory_id,
                "experiment_id": m.metadata.get("experiment_id"),
                "experiment_type": m.metadata.get("experiment_type"),
                "success": m.value.get("success"),
                "reward": m.value.get("reward")
            }
            for m in memories
        ]
    }


@app.get("/api/v1/patterns")
async def get_patterns(pattern_type: Optional[str] = None, core = Depends(get_knowledge_core)):
    """Get detected patterns"""
    from knowledge.engines.pattern_recognition import PatternType
    
    type_filter = PatternType(pattern_type) if pattern_type else None
    patterns = core.knowledge_graph._patterns.values()
    
    if type_filter:
        patterns = [p for p in patterns if p.pattern_type == type_filter]
    
    return {
        "patterns": [
            {
                "pattern_id": p.pattern_id,
                "pattern_type": p.pattern_type.value,
                "name": p.name,
                "confidence": p.confidence,
                "data_points": p.data_points
            }
            for p in patterns
        ]
    }


@app.get("/api/v1/insights")
async def get_insights(category: Optional[str] = None, learning = Depends(get_learning_engine)):
    """Get learning insights"""
    insights = learning.get_insights(category=category)
    
    return {
        "insights": [
            {
                "insight_id": i.insight_id,
                "category": i.category,
                "pattern": i.pattern,
                "confidence": i.confidence,
                "recommendation": i.recommendation
            }
            for i in insights
        ]
    }


@app.get("/api/v1/knowledge-graph")
async def get_knowledge_graph(graph = Depends(get_knowledge_graph)):
    """Get knowledge graph"""
    nodes = [{"node_id": n.node_id, "node_type": n.node_type.value, "label": n.label} for n in graph._nodes.values()]
    edges = [{"edge_id": e.edge_id, "source_id": e.source_id, "target_id": e.target_id, "edge_type": e.edge_type.value} for e in graph._edges]
    
    return {
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "total_nodes": len(nodes),
            "total_edges": len(edges)
        }
    }


@app.get("/api/v1/metrics")
async def get_metrics(metrics = Depends(get_metrics_collector)):
    """Get knowledge platform metrics"""
    return metrics.get_metrics()


@app.get("/api/v1/knowledge/{knowledge_id}/versions")
async def get_knowledge_versions(knowledge_id: str, core = Depends(get_knowledge_core)):
    """Get knowledge version history"""
    history = core.memory_engine._memory.get("long_term", {})
    versions = [v for v in history.values() if v.metadata.get("knowledge_id") == knowledge_id]
    
    return {
        "knowledge_id": knowledge_id,
        "versions": [
            {
                "version_id": v.metadata.get("version_id"),
                "version": v.metadata.get("version"),
                "title": v.metadata.get("title"),
                "author": v.metadata.get("author"),
                "change_reason": v.metadata.get("change_reason"),
                "created_at": v.created_at
            }
            for v in versions
        ]
    }


@app.post("/api/v1/knowledge/record-learning")
async def record_learning_event(event_type: str, source: str, data: Dict[str, Any], outcome: Dict[str, Any], reward: float, context: Dict[str, Any], learning = Depends(get_learning_engine)):
    """Record learning event"""
    from knowledge.engines.learning_engine import LearningEventType
    
    try:
        event_type_enum = LearningEventType(event_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid event type: {event_type}")
    
    event_id = learning.record_event(event_type_enum, source, data, outcome, reward, context)
    
    return {
        "event_id": event_id,
        "event_type": event_type,
        "source": source,
        "reward": reward
    }


@app.get("/api/v1/memory/stats")
async def get_memory_stats(memory = Depends(get_knowledge_core)):
    """Get memory statistics"""
    return memory.memory_engine.get_stats()


@app.get("/api/v1/search/stats")
async def get_search_stats(metrics = Depends(get_metrics_collector)):
    """Get search statistics"""
    return {
        "total_searches": metrics._metrics.search_queries,
        "avg_confidence": metrics._metrics.avg_confidence
    }


def get_knowledge_core():
    from knowledge.core.knowledge_core import KnowledgeCore
    from knowledge.engines.learning_engine import LearningEngine
    from knowledge.engines.memory_engine import MemoryEngine
    from knowledge.engines.knowledge_graph import KnowledgeGraph
    from knowledge.engines.semantic_search import SemanticSearch
    from knowledge.engines.embedding_service import EmbeddingService
    from knowledge.db.knowledge_db import KnowledgeDatabaseManager
    from knowledge.infrastructure.knowledge_versioning import KnowledgeVersioning
    from knowledge.infrastructure.knowledge_audit import KnowledgeAudit
    from shared.database import DatabaseManager
    
    db = DatabaseManager("data/knowledge.db")
    versioning = KnowledgeVersioning(db)
    audit = KnowledgeAudit(db)
    learning_engine = LearningEngine(db)
    memory_engine = MemoryEngine(db)
    embedding_service = EmbeddingService()
    knowledge_graph = KnowledgeGraph(db)
    semantic_search = SemanticSearch(embedding_service, db)
    core = KnowledgeCore(db, learning_engine, memory_engine, knowledge_graph, semantic_search)
    
    return core


def get_knowledge_repository():
    from knowledge.engines.knowledge_repository import KnowledgeRepository
    from knowledge.db.knowledge_db import KnowledgeDatabaseManager
    from knowledge.infrastructure.knowledge_versioning import KnowledgeVersioning
    from knowledge.infrastructure.knowledge_audit import KnowledgeAudit
    from shared.database import DatabaseManager
    
    db = DatabaseManager("data/knowledge.db")
    versioning = KnowledgeVersioning(db)
    audit = KnowledgeAudit(db)
    return KnowledgeRepository(db, versioning, audit)


def get_learning_engine():
    from knowledge.engines.learning_engine import LearningEngine
    from knowledge.db.knowledge_db import KnowledgeDatabaseManager
    from shared.database import DatabaseManager
    
    db = DatabaseManager("data/knowledge.db")
    return LearningEngine(db)


def get_semantic_search():
    from knowledge.engines.semantic_search import SemanticSearch
    from knowledge.engines.embedding_service import EmbeddingService
    from knowledge.db.knowledge_db import KnowledgeDatabaseManager
    from shared.database import DatabaseManager
    
    db = DatabaseManager("data/knowledge.db")
    embedding_service = EmbeddingService()
    return SemanticSearch(embedding_service, db)


def get_knowledge_graph():
    from knowledge.engines.knowledge_graph import KnowledgeGraph
    from knowledge.db.knowledge_db import KnowledgeDatabaseManager
    from shared.database import DatabaseManager
    
    db = DatabaseManager("data/knowledge.db")
    return KnowledgeGraph(db)


def get_metrics_collector():
    from knowledge.infrastructure.knowledge_metrics import KnowledgeMetricsCollector
    return KnowledgeMetricsCollector()
