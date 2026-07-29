#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Marketing Tests
Test suite for marketing engine.
"""

import os
import sys
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai.provider import AIProviderManager, BaseAIProvider, AIConfig, AIMessage, AIProviderType
from core.registry import ContentPipelineStateMachine, ContentStatus
from keywords.engine import KeywordEngine
from quality.engine import ContentQualityEngine
from brand.engine import BrandEngine
from localization.engine import LocalizationEngine
from ab_testing.engine import ABTestingEngine
from assets.engine import AssetGenerationEngine
from pipeline.state_machine import ContentPipeline


# ============ FIXTURES ============

@pytest.fixture
def temp_dir():
    """Create temporary directory"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def db_manager(temp_dir):
    """Create database manager"""
    from core.engine import DatabaseManager
    db_path = temp_dir / "test.db"
    return DatabaseManager(db_path)


@pytest.fixture
def mock_ai_manager():
    """Mock AI manager"""
    manager = AIProviderManager()
    
    class MockProvider(BaseAIProvider):
        PROVIDER_TYPE = AIProviderType.OPENAI
        DEFAULT_MODEL = "gpt-4"
        
        async def generate(self, messages, **kwargs):
            from ai.provider import AIResponse
            return AIResponse(
                content="Generated content",
                provider="mock",
                model="mock-model",
                tokens_used=100,
                latency_ms=500
            )
        
        async def health(self):
            return {"status": "healthy"}
    
    provider = MockProvider(AIConfig(provider="mock"))
    manager.register_provider(provider, AIConfig(provider="mock"), priority=10)
    manager.set_default("mock")
    return manager


# ============ TESTS ============

class TestStateMachine:
    """Test content pipeline state machine"""
    
    def test_valid_transitions(self):
        assert ContentPipelineStateMachine.can_transition("draft", "generating") is True
        assert ContentPipelineStateMachine.can_transition("draft", "archived") is False
    
    def test_invalid_transition(self):
        assert ContentPipelineStateMachine.can_transition("draft", "deleted") is False
    
    def test_valid_transitions_from_generating(self):
        valid = ContentPipelineStateMachine.get_valid_transitions("generating")
        assert "reviewing" in valid
        assert "failed" in valid


class TestKeywordEngine:
    """Test keyword engine"""
    
    def test_discover_keywords(self, mock_ai_manager):
        engine = KeywordEngine(mock_ai_manager)
        product_data = {"title": "Test Product", "category": "digital"}
        keywords = engine.discover_keywords(product_data)
        assert len(keywords) > 0
    
    def test_get_primary_keywords(self):
        engine = KeywordEngine(None)
        from keywords.engine import Keyword
        keywords = [
            Keyword("kw1", "transactional", "medium", "high", 1000, "medium", "en", "", [], ""),
            Keyword("kw2", "informational", "easy", "medium", 500, "low", "en", "", [], "")
        ]
        primary = engine.get_primary_keywords(keywords)
        assert "kw1" in primary
    
    def test_generate_hashtags(self):
        engine = KeywordEngine(None)
        hashtags = engine.generate_hashtags(["marketing", "digital"], "instagram", 5)
        assert len(hashtags) == 5
        assert all(h.startswith("#") for h in hashtags)


class TestContentQualityEngine:
    """Test content quality engine"""
    
    def test_validate_content(self):
        engine = ContentQualityEngine(None)
        report = engine.validate_content("Test content", "product_description", ["test"], {})
        assert "overall_score" in report
        assert "passed" in report
        assert "checks" in report
    
    def test_grammar_check(self):
        engine = ContentQualityEngine(None)
        check = engine._check_grammar("Good content. No issues.")
        assert check.passed is True
    
    def test_length_check(self):
        engine = ContentQualityEngine(None)
        check = engine._check_length("Short", "product_description")
        assert check.passed is False


class TestBrandEngine:
    """Test brand engine"""
    
    def test_create_brand_rules(self, db_manager):
        engine = BrandEngine(db_manager)
        success = engine.create_brand_rules("TestBrand", {
            "voice": "professional",
            "tone": "confident",
            "forbidden_terms": ["bad", "terrible"]
        })
        assert success is True
    
    def test_validate_content(self, db_manager):
        engine = BrandEngine(db_manager)
        engine.create_brand_rules("TestBrand", {"forbidden_terms": ["bad"]})
        result = engine.validate_content("This is bad content", "TestBrand")
        assert result["valid"] is False


class TestLocalizationEngine:
    """Test localization engine"""
    
    def test_get_supported_languages(self):
        engine = LocalizationEngine(None, None)
        languages = engine.get_supported_languages()
        assert "en" in languages
        assert "id" in languages


class TestABTestingEngine:
    """Test A/B testing engine"""
    
    def test_create_test(self, db_manager):
        engine = ABTestingEngine(db_manager)
        test_id = engine.create_test("prod-123", "email", [
            {"subject": "Test A"},
            {"subject": "Test B"}
        ])
        assert test_id is not None
    
    def test_get_test(self, db_manager):
        engine = ABTestingEngine(db_manager)
        test_id = engine.create_test("prod-123", "email", [{"subject": "Test A"}])
        test = engine.get_test(test_id)
        assert test is not None
        assert test.product_id == "prod-123"


class TestAssetGenerationEngine:
    """Test asset generation engine"""
    
    def test_generate_asset_spec(self, db_manager, mock_ai_manager):
        engine = AssetGenerationEngine(db_manager, mock_ai_manager)
        asset = engine.generate_asset_spec("prod-123", "thumbnail", {"title": "Test"})
        assert asset.asset_id is not None
        assert asset.asset_type == "thumbnail"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
