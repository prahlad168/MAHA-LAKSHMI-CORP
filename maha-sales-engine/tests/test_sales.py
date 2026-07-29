#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Sales Automation Tests
Unit and integration tests for the Sales Automation module.
"""

import os
import sys
import json
import pytest
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestLeadScorer:
    """Test lead scorer"""
    
    def test_score_lead(self):
        """Test lead scoring"""
        from sales.lead_scoring import LeadScorer
        
        scorer = LeadScorer()
        score = scorer.score_lead({
            "email": "test@example.com",
            "company": "Test Corp",
            "budget": 50000
        })
        
        assert score is not None
        assert "score" in score
        assert 0 <= score["score"] <= 100


class TestSalesBot:
    """Test sales bot"""
    
    def test_generate_response(self):
        """Test sales bot response generation"""
        from sales.sales_bot import SalesBot
        
        bot = SalesBot()
        response = bot.generate_response(
            message="What are your prices?",
            context={"product": "digital"}
        )
        
        assert response is not None
        assert len(response) > 0


class TestPipeline:
    """Test sales pipeline"""
    
    def test_add_lead(self):
        """Test adding lead to pipeline"""
        from sales.pipeline import Pipeline
        
        pipeline = Pipeline()
        lead = pipeline.add_lead({
            "name": "Test Lead",
            "email": "test@example.com",
            "stage": "qualified"
        })
        
        assert lead is not None
        assert lead["name"] == "Test Lead"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
