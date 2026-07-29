#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Marketing Engine Tests
Unit and integration tests for the Marketing Engine module.
"""

import os
import sys
import json
import pytest
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestContentGenerator:
    """Test content generator"""
    
    def test_generate_blog_post(self):
        """Test blog post generation"""
        from marketing.content_generator import ContentGenerator
        
        generator = ContentGenerator()
        content = generator.generate_blog_post(
            topic="AI Marketing",
            keywords=["AI", "marketing"]
        )
        
        assert content is not None
        assert len(content) > 0


class TestSEOOptimizer:
    """Test SEO optimizer"""
    
    def test_optimize_content(self):
        """Test content optimization"""
        from marketing.seo_optimizer import SEOOptimizer
        
        optimizer = SEOOptimizer()
        result = optimizer.optimize(
            content="Test content about AI marketing",
            keywords=["AI", "marketing"]
        )
        
        assert result is not None
        assert "score" in result


class TestSocialMediaManager:
    """Test social media manager"""
    
    def test_generate_post(self):
        """Test social media post generation"""
        from marketing.social_media import SocialMediaManager
        
        manager = SocialMediaManager()
        post = manager.generate_post(
            platform="twitter",
            content="Check out our new product!"
        )
        
        assert post is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
