#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Knowledge Tests
Tests for Knowledge & Learning Platform.
"""

import os
import sys
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture(scope="function")
def temp_dir():
    """Create temporary directory"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture(scope="function")
def db_manager(temp_dir):
    """Create database manager"""
    from shared.database import DatabaseManager
    db_path = temp_dir / "knowledge.db"
    return DatabaseManager(db_path)


class TestKnowledgeCore:
    """Test knowledge core"""
    
    def test_create_knowledge(self, db_manager):
        from knowledge.core.knowledge_core import KnowledgeCore, KnowledgeType
        from knowledge.engines.learning_engine import LearningEngine
        from knowledge.engines.memory_engine import MemoryEngine
        from knowledge.engines.knowledge_graph import KnowledgeGraph
        from knowledge.engines.semantic_search import SemanticSearch
        from knowledge.engines.embedding_service import EmbeddingService
        from knowledge.infrastructure.knowledge_versioning import KnowledgeVersioning
        from knowledge.infrastructure.knowledge_audit import KnowledgeAudit
        
        versioning = KnowledgeVersioning(db_manager)
        audit = KnowledgeAudit(db_manager)
        learning_engine = LearningEngine(db_manager)
        memory_engine = MemoryEngine(db_manager)
        embedding_service = EmbeddingService()
        knowledge_graph = KnowledgeGraph(db_manager)
        semantic_search = SemanticSearch(embedding_service, db_manager)
        core = KnowledgeCore(db_manager, learning_engine, memory_engine, knowledge_graph, semantic_search)
        
        context = core.create_knowledge(
            knowledge_type=KnowledgeType.DOCUMENT,
            title="Test Knowledge",
            content={"key": "value"},
            source="test"
        )
        
        assert context.knowledge_id is not None
        assert context.title == "Test Knowledge"
        assert context.version == 1


class TestLearningEngine:
    """Test learning engine"""
    
    def test_record_event(self, db_manager):
        from knowledge.engines.learning_engine import LearningEngine, LearningEventType
        
        engine = LearningEngine(db_manager)
        event_id = engine.record_event(
            event_type=LearningEventType.OPTIMIZATION_EXECUTED,
            source="test",
            data={"category": "pricing"},
            outcome={"success": True},
            reward=0.8,
            context={"category": "pricing"}
        )
        
        assert event_id is not None
        performance = engine.get_performance("pricing")
        assert performance["avg_reward"] == 0.8
    
    def test_generate_insights(self, db_manager):
        from knowledge.engines.learning_engine import LearningEngine, LearningEventType
        
        engine = LearningEngine(db_manager)
        
        # Record multiple events
        for i in range(10):
            engine.record_event(
                event_type=LearningEventType.OPTIMIZATION_EXECUTED,
                source="test",
                data={"category": "marketing"},
                outcome={"success": True},
                reward=0.8,
                context={"category": "marketing"}
            )
        
        insights = engine.get_insights("marketing")
        assert len(insights) > 0


class TestMemoryEngine:
    """Test memory engine"""
    
    def test_store_and_retrieve(self, db_manager):
        from knowledge.engines.memory_engine import MemoryEngine, MemoryType
        
        engine = MemoryEngine(db_manager)
        engine.store(MemoryType.SHORT_TERM, "test_key", "test_value", ttl=60)
        
        item = engine.retrieve(MemoryType.SHORT_TERM, "test_key")
        assert item is not None
        assert item.value == "test_value"
    
    def test_memory_expiry(self, db_manager):
        from knowledge.engines.memory_engine import MemoryEngine, MemoryType
        import time
        
        engine = MemoryEngine(db_manager)
        engine.store(MemoryType.SHORT_TERM, "expiring_key", "value", ttl=1)
        
        time.sleep(1.1)
        item = engine.retrieve(MemoryType.SHORT_TERM, "expiring_key")
        assert item is None
    
    def test_memory_stats(self, db_manager):
        from knowledge.engines.memory_engine import MemoryEngine, MemoryType
        
        engine = MemoryEngine(db_manager)
        engine.store(MemoryType.SHORT_TERM, "key1", "value1")
        engine.store(MemoryType.LONG_TERM, "key2", "value2")
        
        stats = engine.get_stats()
        assert "short_term" in stats
        assert "long_term" in stats


class TestKnowledgeGraph:
    """Test knowledge graph"""
    
    def test_add_nodes_and_edges(self, db_manager):
        from knowledge.engines.knowledge_graph import KnowledgeGraph, NodeType, EdgeType
        
        graph = KnowledgeGraph(db_manager)
        node1 = graph.add_node(NodeType.PRODUCT, "Product A", {"price": 100})
        node2 = graph.add_node(NodeType.CUSTOMER, "Customer A", {"email": "test@example.com"})
        edge = graph.add_edge(node1.node_id, node2.node_id, EdgeType.PURCHASED, {"date": "2024-01-01"})
        
        assert node1.node_id is not None
        assert node2.node_id is not None
        assert edge.edge_id is not None
    
    def test_find_path(self, db_manager):
        from knowledge.engines.knowledge_graph import KnowledgeGraph, NodeType, EdgeType
        
        graph = KnowledgeGraph(db_manager)
        node1 = graph.add_node(NodeType.PRODUCT, "Product A", {})
        node2 = graph.add_node(NodeType.ORDER, "Order A", {})
        node3 = graph.add_node(NodeType.CUSTOMER, "Customer A", {})
        
        graph.add_edge(node1.node_id, node2.node_id, EdgeType.OPTIMIZED)
        graph.add_edge(node2.node_id, node3.node_id, EdgeType.GENERATED)
        
        path = graph.find_path(node1.node_id, node3.node_id)
        assert path is not None
        assert len(path) == 2


class TestSemanticSearch:
    """Test semantic search"""
    
    def test_index_and_search(self, db_manager):
        from knowledge.engines.semantic_search import SemanticSearch
        from knowledge.engines.embedding_service import EmbeddingService
        
        embedding_service = EmbeddingService()
        search = SemanticSearch(embedding_service, db_manager)
        
        search.index_document("doc1", "Product pricing optimization", {"source": "optimization"})
        search.index_document("doc2", "Marketing campaign analysis", {"source": "marketing"})
        
        results = search.search("pricing optimization")
        assert len(results) > 0
        assert results[0].knowledge_id == "doc1"


class TestPatternRecognition:
    """Test pattern recognition"""
    
    def test_detect_trend(self, db_manager):
        from knowledge.engines.pattern_recognition import PatternRecognition
        
        engine = PatternRecognition(db_manager)
        values = [100, 110, 120, 130, 140]
        pattern = engine.detect_trend("revenue", values)
        
        assert pattern is not None
        assert pattern.pattern_type.value == "trend"
    
    def test_detect_anomaly(self, db_manager):
        from knowledge.engines.pattern_recognition import PatternRecognition
        
        engine = PatternRecognition(db_manager)
        historical = [100, 101, 99, 100, 102]
        current = 150
        pattern = engine.detect_anomaly("revenue", current, historical)
        
        assert pattern is not None
        assert pattern.pattern_type.value == "anomaly"


class TestKnowledgeVersioning:
    """Test knowledge versioning"""
    
    def test_create_versions(self, db_manager):
        from knowledge.infrastructure.knowledge_versioning import KnowledgeVersioning
        
        versioning = KnowledgeVersioning(db_manager)
        v1 = versioning.create_version("know-1", "Title", {"content": "v1"}, "author1", "initial")
        v2 = versioning.create_version("know-1", "Title", {"content": "v2"}, "author2", "update")
        
        assert v1.version == 1
        assert v2.version == 2
        
        history = versioning.get_history("know-1")
        assert len(history) == 2
    
    def test_get_latest(self, db_manager):
        from knowledge.infrastructure.knowledge_versioning import KnowledgeVersioning
        
        versioning = KnowledgeVersioning(db_manager)
        versioning.create_version("know-1", "Title", {"content": "v1"}, "author1", "initial")
        versioning.create_version("know-1", "Title", {"content": "v2"}, "author2", "update")
        
        latest = versioning.get_latest("know-1")
        assert latest.version == 2


class TestDecisionMemory:
    """Test decision memory"""
    
    def test_store_and_update(self, db_manager):
        from knowledge.engines.decision_memory import DecisionMemoryEngine
        
        engine = DecisionMemoryEngine(db_manager)
        memory = engine.store(
            decision_id="dec-1",
            optimization_id="opt-1",
            category="pricing",
            decision="approve",
            reason="High confidence",
            evidence={"metric": "value"},
            confidence=0.9,
            risk_score=0.2
        )
        
        assert memory.decision == "approve"
        
        engine.update_outcome(memory.memory_id, {"revenue": 1000}, 0.9)
        updated = engine.get(memory.memory_id)
        assert updated.reward == 0.9


class TestExperimentMemory:
    """Test experiment memory"""
    
    def test_store_and_retrieve(self, db_manager):
        from knowledge.engines.experiment_memory import ExperimentMemoryEngine
        
        engine = ExperimentMemoryEngine(db_manager)
        memory = engine.store(
            experiment_id="exp-1",
            optimization_id="opt-1",
            experiment_type="a_b_test",
            config={"variant_a": "control", "variant_b": "treatment"},
            results={"winner": "variant_b"},
            success=True,
            reward=0.85
        )
        
        assert memory.success is True
        assert memory.reward == 0.85
        
        experiments = engine.get_by_type("a_b_test")
        assert len(experiments) == 1


class TestKnowledgeValidator:
    """Test knowledge validator"""
    
    def test_valid_knowledge(self):
        from knowledge.engines.knowledge_validator import KnowledgeValidator
        
        validator = KnowledgeValidator()
        result = validator.validate({
            "title": "Test Knowledge",
            "content": "This is valid content",
            "source": "optimization"
        })
        
        assert result.is_valid is True
        assert result.score > 0.5
    
    def test_invalid_knowledge(self):
        from knowledge.engines.knowledge_validator import KnowledgeValidator
        
        validator = KnowledgeValidator()
        result = validator.validate({
            "title": "Test",
            "source": "invalid_source"
        })
        
        assert result.is_valid is False
        assert len(result.issues) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
