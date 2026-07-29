#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Product Factory Tests
Unit and integration tests.
"""

import os
import sys
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.engine import ConfigManager, DatabaseManager
from product_factory.core.factory import ProductFactory, ProductStatus, ProductCategory
from product_factory.generators.engine import ProductGeneratorFactory, EbookGenerator
from product_factory.quality.engine import QualityEngine
from product_factory.versioning.manager import VersionManager
from product_factory.packaging.packager import ProductPackager
from product_factory.licenses.manager import LicenseManager
from product_factory.reports.reporter import ProductFactoryReports


# ============ FIXTURES ============

@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def db_manager(temp_dir):
    """Create database manager"""
    db_path = temp_dir / "test.db"
    return DatabaseManager(db_path)


@pytest.fixture
def config(temp_dir):
    """Create config manager"""
    config_data = {
        "database": {"path": str(temp_dir / "test.db")},
        "product_factory": {"output_dir": str(temp_dir / "output")}
    }
    config_path = temp_dir / "config.yaml"
    import yaml
    with open(config_path, "w") as f:
        yaml.dump(config_data, f)
    return ConfigManager(config_path)


@pytest.fixture
def factory(db_manager, config):
    """Create product factory"""
    return ProductFactory(db_manager, config)


@pytest.fixture
def output_dir(temp_dir):
    """Create output directory"""
    output = temp_dir / "output"
    output.mkdir(exist_ok=True)
    return output


# ============ TESTS ============

class TestProductFactory:
    """Test ProductFactory core"""
    
    def test_create_product(self, factory):
        """Test product creation"""
        product_id = factory.create_product(
            title="Test Product",
            category=ProductCategory.EBOOK.value,
            description="Test description",
            price_usd=19.0,
            price_idr=285000
        )
        
        assert product_id is not None
        assert product_id.startswith("ML-")
        
        product = factory.get_product(product_id)
        assert product["title"] == "Test Product"
        assert product["status"] == ProductStatus.IDEA.value
    
    def test_list_products(self, factory):
        """Test listing products"""
        factory.create_product("Product 1", ProductCategory.EBOOK.value)
        factory.create_product("Product 2", ProductCategory.TEMPLATE.value)
        
        products = factory.list_products(limit=10)
        assert len(products) >= 2
    
    def test_update_status(self, factory):
        """Test status update"""
        product_id = factory.create_product("Test", ProductCategory.EBOOK.value)
        success = factory.update_product_status(product_id, ProductStatus.GENERATING.value)
        
        assert success is True
        product = factory.get_product(product_id)
        assert product["status"] == ProductStatus.GENERATING.value
    
    def test_get_stats(self, factory):
        """Test statistics"""
        stats = factory.get_stats()
        assert "total_products" in stats
        assert "by_status" in stats
        assert "by_category" in stats


class TestGenerators:
    """Test product generators"""
    
    def test_ebook_generator(self, output_dir):
        """Test eBook generation"""
        generator = EbookGenerator(output_dir)
        result = generator.generate(
            product_id="ML-TEST-001",
            title="Test eBook",
            description="Test description"
        )
        
        assert "error" not in result
        assert result["product_id"] == "ML-TEST-001"
        assert result["status"] == "generated"
        
        # Verify files
        product_dir = output_dir / "ML-TEST-001"
        assert (product_dir / "metadata.json").exists()
        assert (product_dir / "description.md").exists()
        assert (product_dir / "license.txt").exists()
        assert (product_dir / "product").exists()
    
    def test_generator_factory(self, output_dir):
        """Test generator factory"""
        gen_factory = ProductGeneratorFactory(output_dir)
        
        generators = gen_factory.get_supported_categories()
        assert "ebook" in generators
        assert "template" in generators
        assert "prompt_pack" in generators


class TestQualityEngine:
    """Test quality engine"""
    
    def test_quality_check(self, output_dir):
        """Test quality check"""
        engine = QualityEngine(output_dir)
        
        # Create a test product first
        generator = EbookGenerator(output_dir)
        generator.generate(
            product_id="ML-QUALITY-001",
            title="Quality Test",
            description="Test"
        )
        
        report = engine.run_quality_check("ML-QUALITY-001")
        
        assert "overall_score" in report
        assert "passed" in report
        assert "checks" in report
    
    def test_quality_check_nonexistent(self, output_dir):
        """Test quality check on non-existent product"""
        engine = QualityEngine(output_dir)
        report = engine.run_quality_check("ML-NONEXISTENT")
        
        assert "error" in report


class TestVersionManager:
    """Test version manager"""
    
    def test_create_version(self, output_dir, db_manager):
        """Test version creation"""
        version_manager = VersionManager(output_dir, db_manager)
        
        # Create product
        generator = EbookGenerator(output_dir)
        generator.generate(
            product_id="ML-VER-001",
            title="Version Test",
            description="Test"
        )
        
        version_id = version_manager.create_version(
            "ML-VER-001",
            output_dir / "ML-VER-001",
            "Initial version"
        )
        
        assert version_id is not None
        assert version_id.startswith("VER-")
        
        # Verify version directory
        version_dir = output_dir / "ML-VER-001" / "versions" / version_id
        assert version_dir.exists()
    
    def test_get_version_history(self, output_dir, db_manager):
        """Test version history"""
        version_manager = VersionManager(output_dir, db_manager)
        
        history = version_manager.get_version_history("ML-VER-001")
        assert isinstance(history, list)


class TestPackager:
    """Test packager"""
    
    def test_create_zip(self, output_dir):
        """Test ZIP creation"""
        packager = ProductPackager(output_dir)
        
        # Create product
        generator = EbookGenerator(output_dir)
        generator.generate(
            product_id="ML-PKG-001",
            title="Package Test",
            description="Test"
        )
        
        zip_path = packager.create_zip_package("ML-PKG-001", output_dir / "ML-PKG-001")
        
        assert zip_path is not None
        assert zip_path.endswith(".zip")
        assert Path(zip_path).exists()
    
    def test_create_manifest(self, output_dir):
        """Test manifest creation"""
        packager = ProductPackager(output_dir)
        
        generator = EbookGenerator(output_dir)
        generator.generate(
            product_id="ML-MANIFEST-001",
            title="Manifest Test",
            description="Test"
        )
        
        manifest = packager.create_manifest(
            "ML-MANIFEST-001",
            output_dir / "ML-MANIFEST-001",
            ""
        )
        
        assert "product_id" in manifest
        assert "files" in manifest
        assert manifest["total_files"] > 0


class TestLicenseManager:
    """Test license manager"""
    
    def test_get_license(self, db_manager):
        """Test getting license"""
        manager = LicenseManager(db_manager)
        
        license_data = manager.get_license("commercial")
        assert license_data["name"] == "Commercial Use License"
        assert "terms" in license_data
    
    def test_create_license(self, db_manager):
        """Test creating license"""
        manager = LicenseManager(db_manager)
        
        success = manager.create_license("ML-LIC-001", "commercial")
        assert success is True


class TestReports:
    """Test reports"""
    
    def test_daily_report(self, output_dir, db_manager):
        """Test daily report"""
        reports = ProductFactoryReports(db_manager, output_dir)
        
        report = reports.generate_daily_report()
        
        assert "report_date" in report
        assert "summary" in report


# ============ INTEGRATION TESTS ============

class TestIntegration:
    """Integration tests"""
    
    def test_full_lifecycle(self, output_dir, db_manager):
        """Test full product lifecycle"""
        factory = ProductFactory(db_manager, ConfigManager(Path("config/engine.yaml")))
        generator_factory = ProductGeneratorFactory(output_dir)
        quality_engine = QualityEngine(output_dir)
        version_manager = VersionManager(output_dir, db_manager)
        packager = ProductPackager(output_dir)
        
        # Create
        product_id = factory.create_product(
            title="Integration Test",
            category=ProductCategory.EBOOK.value
        )
        assert product_id is not None
        
        # Generate
        generator = generator_factory.get_generator("ebook")
        result = generator.generate(product_id, "Integration Test", "Test")
        assert "error" not in result
        
        # Quality check
        quality = quality_engine.run_quality_check(product_id)
        assert quality["passed"] is True
        
        # Version
        version_id = version_manager.create_version(
            product_id,
            output_dir / product_id,
            "Initial version"
        )
        assert version_id is not None
        
        # Package
        zip_path = packager.create_zip_package(product_id, output_dir / product_id)
        assert zip_path is not None
        
        # Update status
        factory.update_product_status(product_id, ProductStatus.PACKAGED.value)
        product = factory.get_product(product_id)
        assert product["status"] == ProductStatus.PACKAGED.value


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
