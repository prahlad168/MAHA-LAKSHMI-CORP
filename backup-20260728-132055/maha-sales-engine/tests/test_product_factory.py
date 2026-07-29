#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Product Factory Tests
Unit and integration tests for the Product Factory module.
"""

import os
import sys
import json
import pytest
import tempfile
from pathlib import Path
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestProductGenerator:
    """Test product generator"""
    
    def test_generate_digital_product(self):
        """Test digital product generation"""
        from product_factory.generator import ProductGenerator
        
        generator = ProductGenerator()
        product = generator.generate_product(
            product_type="ebook",
            title="Test Book",
            description="A test book"
        )
        
        assert product is not None
        assert product.get("title") == "Test Book"
    
    def test_generate_course(self):
        """Test course generation"""
        from product_factory.generator import ProductGenerator
        
        generator = ProductGenerator()
        course = generator.generate_course(
            title="Test Course",
            modules=["Module 1", "Module 2"]
        )
        
        assert course is not None
        assert len(course.get("modules", [])) == 2


class TestProductManager:
    """Test product manager"""
    
    def test_create_product(self):
        """Test product creation"""
        from product_factory.manager import ProductManager
        from shared.database import DatabaseManager
        
        db_path = tempfile.mktemp(suffix=".db")
        db = DatabaseManager(db_path)
        
        try:
            manager = ProductManager(db)
            product = manager.create_product({
                "title": "Test Product",
                "type": "digital",
                "price": 29.99
            })
            
            assert product is not None
            assert product["title"] == "Test Product"
        finally:
            db.close()
            Path(db_path).unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
