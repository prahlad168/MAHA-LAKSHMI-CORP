#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Product Factory Main
Orchestrates all product factory components.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.engine import ConfigManager, DatabaseManager
from product_factory.core.factory import ProductFactory, ProductStatus, ProductCategory
from product_factory.generators.engine import ProductGeneratorFactory
from product_factory.quality.engine import QualityEngine
from product_factory.versioning.manager import VersionManager
from product_factory.packaging.packager import ProductPackager
from product_factory.licenses.manager import LicenseManager
from product_factory.reports.reporter import ProductFactoryReports

logger = logging.getLogger("maha-sales-engine.product-factory")


class ProductFactoryMain:
    """Main orchestrator for Product Factory"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.output_dir = base_dir / "product-factory" / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize components
        config_path = base_dir / "config" / "engine.yaml"
        self.config = ConfigManager(config_path)
        self.db = DatabaseManager(Path(self.config.get("database.path")))
        
        self.factory = ProductFactory(self.db, self.config)
        self.generator_factory = ProductGeneratorFactory(self.output_dir)
        self.quality_engine = QualityEngine(self.output_dir)
        self.version_manager = VersionManager(self.output_dir, self.db)
        self.packager = ProductPackager(self.output_dir)
        self.license_manager = LicenseManager(self.db)
        self.reporter = ProductFactoryReports(self.db, self.output_dir)
        
        logger.info("Product Factory Main initialized")
    
    def create_product(self, title: str, category: str, description: str = "", **kwargs) -> Optional[str]:
        """Create a new product"""
        return self.factory.create_product(title, category, description, **kwargs)
    
    def generate_product(self, product_id: str, generator_type: str, **kwargs) -> Dict[str, Any]:
        """Generate product package"""
        generator = self.generator_factory.get_generator(generator_type)
        if not generator:
            return {"error": f"Unsupported generator: {generator_type}"}
        
        # Update status
        self.factory.update_product_status(product_id, ProductStatus.GENERATING.value)
        
        # Generate product
        result = generator.generate(
            product_id=product_id,
            title=kwargs.get("title", "Untitled Product"),
            description=kwargs.get("description", ""),
            **kwargs
        )
        
        if "error" in result:
            self.factory.update_product_status(product_id, ProductStatus.IDEA.value)
            return result
        
        # Create version
        version_id = self.version_manager.create_version(
            product_id,
            self.output_dir / product_id,
            f"Generated {generator_type}"
        )
        
        # Run quality check
        quality_report = self.quality_engine.run_quality_check(product_id)
        
        # Create license
        license_type = kwargs.get("license", "personal")
        self.license_manager.create_license(product_id, license_type)
        
        # Update status based on quality
        if quality_report.get("passed", False):
            self.factory.update_product_status(product_id, ProductStatus.REVIEW.value)
        else:
            self.factory.update_product_status(product_id, ProductStatus.GENERATING.value)
        
        return {
            "product_id": product_id,
            "generator": generator_type,
            "result": result,
            "quality_passed": quality_report.get("passed", False),
            "quality_score": quality_report.get("overall_score", 0),
            "version_id": version_id
        }
    
    def package_product(self, product_id: str, format: str = "zip") -> Dict[str, Any]:
        """Package product for distribution"""
        product_dir = self.output_dir / product_id
        if not product_dir.exists():
            return {"error": "Product not found"}
        
        if format == "zip":
            package_path = self.packager.create_zip_package(product_id, product_dir)
        elif format == "folder":
            package_path = self.packager.create_folder_export(product_id, product_dir)
        else:
            return {"error": "Invalid format"}
        
        if not package_path:
            return {"error": "Failed to create package"}
        
        manifest = self.packager.create_manifest(product_id, product_dir, package_path)
        
        # Update status
        self.factory.update_product_status(product_id, ProductStatus.PACKAGED.value)
        
        return {
            "product_id": product_id,
            "format": format,
            "package_path": package_path,
            "manifest": manifest
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get factory statistics"""
        return self.factory.get_stats()
    
    def get_status(self) -> Dict[str, Any]:
        """Get module status"""
        return self.factory.get_status()


def main():
    """Test Product Factory Main"""
    from pathlib import Path
    
    base_dir = Path(__file__).parent.parent.parent
    main = ProductFactoryMain(base_dir)
    
    # Test creating a product
    product_id = main.create_product(
        title="Social Media Content Pack",
        category=ProductCategory.SOCIAL_MEDIA_CONTENT_PACK.value,
        description="500+ social media templates",
        price_usd=29.0,
        price_idr=435000
    )
    
    if product_id:
        print(f"Product created: {product_id}")
        
        # Test generation
        result = main.generate_product(
            product_id,
            "template",
            title="Social Media Content Pack",
            description="500+ social media templates",
            template_type="html"
        )
        print(f"Generation result: {result.get('status', 'unknown')}")
        
        # Test packaging
        package = main.package_product(product_id, "zip")
        print(f"Package created: {package.get('package_path', 'failed')}")
    
    # Get stats
    stats = main.get_stats()
    print(f"\nFactory Stats: {stats}")


if __name__ == "__main__":
    main()
