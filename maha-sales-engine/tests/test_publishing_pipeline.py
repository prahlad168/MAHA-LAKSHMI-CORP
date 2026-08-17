#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Publishing Pipeline Integration Test
Tests the complete publishing pipeline: Generate → Package → Publish → Record → Analytics
"""

import os
import sys
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))


def skip_if_no_gumroad_key():
    if not os.getenv("GUMROAD_API_KEY"):
        pytest.skip("GUMROAD_API_KEY not set, skipping real publishing pipeline test")


class TestPublishingPipeline:
    """Integration test for complete publishing pipeline"""
    
    def setup_method(self):
        """Setup test environment"""
        skip_if_no_gumroad_key()
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create necessary directories
        Path("product-factory/output").mkdir(parents=True, exist_ok=True)
        Path("product-factory/output/packages").mkdir(parents=True, exist_ok=True)
        Path("db").mkdir(parents=True, exist_ok=True)
        Path("config").mkdir(parents=True, exist_ok=True)
        
        # Create minimal engine.yaml
        config_yaml = """
engine:
  name: "Test Engine"
  version: "1.0.0"
database:
  path: "./db/maha_sales_engine.db"
marketplaces:
  gumroad:
    enabled: true
    api_key: ""
"""
        with open("config/engine.yaml", "w") as f:
            f.write(config_yaml)
    
    def teardown_method(self):
        """Cleanup test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_end_to_end_publishing_pipeline(self):
        """Test complete publishing pipeline"""
        from publishing_pipeline import PublishingPipeline
        from core.engine import ConfigManager, DatabaseManager
        
        config = ConfigManager(Path("config/engine.yaml"))
        db = DatabaseManager(Path(config.get("database.path")))
        
        pipeline = PublishingPipeline(config, db)
        
        # Product specification
        product_spec = {
            "title": "Test Digital Product",
            "description": "A test digital product for integration testing",
            "short_description": "Test digital product",
            "long_description": "This is a complete test digital product for integration testing of the publishing pipeline.",
            "category": "ebook",
            "tags": ["test", "digital", "product"],
            "price_usd": 19.99,
            "price_idr": 285000,
            "license": "commercial",
            "target_market": "global"
        }
        
        # Run pipeline
        import asyncio
        result = asyncio.run(pipeline.run(product_spec))
        
        # Verify result
        assert result["success"] is True
        assert result["product_id"] is not None
        assert result["marketplace"] == "gumroad"
        assert result["publish_time"] is not None
        assert result["publish_status"] == "published"
        
        # Verify product was created
        product = pipeline.product_factory.get_product(result["product_id"])
        assert product is not None
        assert product["title"] == "Test Digital Product"
        assert product["category"] == "ebook"
        
        # Verify package was created
        packages = pipeline.packager.list_packages()
        assert len(packages) > 0
        assert any(result["product_id"] in p["product_id"] for p in packages)
        
        # Verify publication record was saved
        cursor = db.get_connection().cursor()
        cursor.execute(
            "SELECT * FROM publications WHERE product_id = ?",
            (result["product_id"],)
        )
        pub_record = cursor.fetchone()
        assert pub_record is not None
        assert pub_record["marketplace"] == "gumroad"
        assert pub_record["publish_status"] == "published"
        
        # Verify analytics was recorded
        cursor.execute(
            "SELECT * FROM transactions WHERE product_id = ?",
            (result["product_id"],)
        )
        txn_record = cursor.fetchone()
        assert txn_record is not None
        assert txn_record["gateway"] == "gumroad"
        assert txn_record["status"] == "published"
        
        db.close()
    
    def test_pipeline_steps(self):
        """Test individual pipeline steps"""
        from publishing_pipeline import PublishingPipeline
        from core.engine import ConfigManager, DatabaseManager
        
        config = ConfigManager(Path("config/engine.yaml"))
        db = DatabaseManager(Path(config.get("database.path")))
        
        pipeline = PublishingPipeline(config, db)
        
        # Test product generation
        product_spec = {
            "title": "Step Test Product",
            "description": "Testing individual steps",
            "category": "ebook",
            "tags": ["test"],
            "price_usd": 9.99
        }
        
        product_id = pipeline._generate_product(product_spec)
        assert product_id is not None
        
        # Test packaging
        zip_path = pipeline._package_product(product_id)
        assert Path(zip_path).exists()
        
        # Test metadata generation
        metadata = pipeline._get_metadata(product_id, product_spec)
        assert metadata["title"] == "Step Test Product"
        assert metadata["price"] == 9.99
        assert len(metadata["tags"]) > 0
        
        # Test cover generation
        cover_path = pipeline._generate_cover(product_id)
        assert Path(cover_path).exists()
        
        # Test validation
        validation = pipeline._validate_metadata(product_id, metadata)
        assert "valid" in validation
        
        db.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
