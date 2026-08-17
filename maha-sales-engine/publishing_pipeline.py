#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Publishing Pipeline
End-to-end pipeline: Generate → Package → Publish → Record → Analytics
"""

import os
import sys
import json
import time
import uuid
import logging
import zipfile
import shutil
import importlib.util
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent))

from core.engine import ConfigManager, DatabaseManager
from marketplace_connector.providers.gumroad.gumroad_provider import GumroadProvider
from marketplace_connector.publication.publication_pipeline import PublicationPipeline
from marketplace_connector.publication.validation_engine import ValidationEngine
from analytics.engine import Analytics

logger = logging.getLogger("maha-sales-engine.publishing_pipeline")


def _load_product_factory_module():
    """Load ProductFactory from product-factory directory (hyphenated name)"""
    base_dir = Path(__file__).parent
    factory_path = base_dir / "product-factory" / "core" / "factory.py"
    
    spec = importlib.util.spec_from_file_location("product_factory_core", factory_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["product_factory_core"] = module
    spec.loader.exec_module(module)
    return module


def _load_generator_module():
    """Load ProductGeneratorFactory from product-factory directory"""
    base_dir = Path(__file__).parent
    generator_path = base_dir / "product-factory" / "generators" / "engine.py"
    
    spec = importlib.util.spec_from_file_location("product_factory_generators", generator_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["product_factory_generators"] = module
    spec.loader.exec_module(module)
    return module


def _load_packager_module():
    """Load ProductPackager from product-factory directory"""
    base_dir = Path(__file__).parent
    packager_path = base_dir / "product-factory" / "packaging" / "packager.py"
    
    spec = importlib.util.spec_from_file_location("product_factory_packager", packager_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["product_factory_packager"] = module
    spec.loader.exec_module(module)
    return module


class PublishingPipeline:
    """End-to-end publishing pipeline"""
    
    def __init__(self, config: ConfigManager, db: DatabaseManager):
        self.config = config
        self.db = db
        self.output_dir = Path("product-factory/output")
        self.output_dir.mkdir(exist_ok=True)
        self.packages_dir = self.output_dir / "packages"
        self.packages_dir.mkdir(exist_ok=True)
        
        # Load product factory modules
        factory_module = _load_product_factory_module()
        generator_module = _load_generator_module()
        packager_module = _load_packager_module()
        
        # Initialize components
        self.product_factory = factory_module.ProductFactory(db, config)
        self.generator_factory = generator_module.ProductGeneratorFactory(self.output_dir)
        self.packager = packager_module.ProductPackager(self.output_dir)
        self.analytics = Analytics(config, db)
        
        # Gumroad provider
        gumroad_config = config.get("marketplaces.gumroad", {})
        self.gumroad_provider = GumroadProvider(gumroad_config)
        
        # Publication pipeline components
        self.validation_engine = ValidationEngine()
        self.publication_pipeline = PublicationPipeline(
            self.gumroad_provider,
            self.validation_engine,
            None  # db_manager - not strictly needed for pipeline execution
        )
    
    async def run(self, product_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Run the complete publishing pipeline"""
        result = {
            "success": False,
            "product_id": None,
            "marketplace": "gumroad",
            "product_url": None,
            "publish_time": None,
            "publish_status": None,
            "steps": {}
        }
        
        try:
            # Step 1: Generate product
            logger.info("Step 1: Generating product...")
            product_id = self._generate_product(product_spec)
            result["product_id"] = product_id
            result["steps"]["generate"] = {"success": True, "product_id": product_id}
            
            # Step 2: Package product
            logger.info("Step 2: Packaging product...")
            package_path = self._package_product(product_id)
            result["steps"]["package"] = {"success": True, "package_path": package_path}
            
            # Step 3: Generate/validate metadata
            logger.info("Step 3: Validating metadata...")
            metadata = self._get_metadata(product_id, product_spec)
            validation = self._validate_metadata(product_id, metadata)
            result["steps"]["validate"] = {"success": validation.get("valid", False), "validation": validation}
            
            # Step 4: Generate cover image (placeholder)
            logger.info("Step 4: Generating cover image...")
            cover_path = self._generate_cover(product_id)
            result["steps"]["cover"] = {"success": True, "cover_path": cover_path}
            
            # Step 5: Publish to Gumroad
            logger.info("Step 5: Publishing to Gumroad...")
            publish_result = await self._publish_to_gumroad(product_id, metadata, package_path, cover_path)
            result["steps"]["publish"] = publish_result
            result["product_url"] = publish_result.get("product_url")
            result["publish_time"] = publish_result.get("publish_time")
            result["publish_status"] = publish_result.get("status")
            
            if publish_result.get("success"):
                result["success"] = True
                
                # Step 6: Save publication record
                logger.info("Step 6: Saving publication record...")
                self._save_publication_record(product_id, publish_result)
                result["steps"]["save_record"] = {"success": True}
                
                # Step 7: Record in Analytics
                logger.info("Step 7: Recording in Analytics...")
                self._record_analytics(product_id, publish_result)
                result["steps"]["analytics"] = {"success": True}
            
            return result
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            result["error"] = str(e)
            return result
    
    def _generate_product(self, product_spec: Dict[str, Any]) -> str:
        """Generate a digital product"""
        # Create product in factory DB
        title = product_spec.get("title", "Untitled Product")
        category = product_spec.get("category", "ebook")
        description = product_spec.get("description", "")
        
        # Map category string to ProductCategory enum
        factory_module = _load_product_factory_module()
        ProductCategory = factory_module.ProductCategory
        
        category_map = {
            "ebook": ProductCategory.EBOOK,
            "template": ProductCategory.TEMPLATE,
            "prompt_pack": ProductCategory.PROMPT_PACK,
            "checklist": ProductCategory.CHECKLIST,
            "mini_course": ProductCategory.MINI_COURSE,
            "social_media_content_pack": ProductCategory.SOCIAL_MEDIA_CONTENT_PACK,
            "business_document": ProductCategory.BUSINESS_DOCUMENT,
            "sop_package": ProductCategory.SOP_PACKAGE
        }
        
        product_category = category_map.get(category, ProductCategory.EBOOK)
        
        product_id = self.product_factory.create_product(
            title=title,
            category=product_category.value,
            description=description,
            price_usd=product_spec.get("price_usd", 19.0),
            price_idr=product_spec.get("price_idr", 285000),
            tags=product_spec.get("tags", []),
            target_market=product_spec.get("target_market", "global"),
            license_type=product_spec.get("license", "commercial")
        )
        
        if not product_id:
            raise Exception("Failed to create product in factory")
        
        # Generate product files using generator
        generator = self.generator_factory.get_generator(category)
        if not generator:
            raise Exception(f"Unsupported category: {category}")
        
        generation_result = generator.generate(
            product_id=product_id,
            title=title,
            description=description,
            price_usd=product_spec.get("price_usd", 19.0),
            price_idr=product_spec.get("price_idr", 285000),
            tags=product_spec.get("tags", [title]),
            license=product_spec.get("license", "commercial"),
            template_type=product_spec.get("template_type", "html")
        )
        
        if "error" in generation_result:
            raise Exception(f"Generation failed: {generation_result['error']}")
        
        logger.info(f"Product generated: {product_id}")
        return product_id
    
    def _package_product(self, product_id: str) -> str:
        """Package product into ZIP"""
        product_dir = self.output_dir / product_id
        if not product_dir.exists():
            raise Exception(f"Product directory not found: {product_dir}")
        
        zip_path = self.packager.create_zip_package(product_id, product_dir)
        if not zip_path:
            raise Exception("Failed to create ZIP package")
        
        # Also create manifest
        self.packager.create_manifest(product_id, product_dir, zip_path)
        
        logger.info(f"Product packaged: {zip_path}")
        return zip_path
    
    def _get_metadata(self, product_id: str, product_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Get or generate product metadata"""
        product_dir = self.output_dir / product_id
        metadata_path = product_dir / "metadata.json"
        
        if metadata_path.exists():
            with open(metadata_path) as f:
                metadata = json.load(f)
        else:
            metadata = {}
        
        # Ensure required fields
        metadata.setdefault("product_id", product_id)
        metadata.setdefault("title", product_spec.get("title", "Untitled Product"))
        metadata.setdefault("description", product_spec.get("description", ""))
        metadata.setdefault("short_description", product_spec.get("short_description", metadata.get("description", "")[:100]))
        metadata.setdefault("long_description", product_spec.get("long_description", metadata.get("description", "")))
        metadata.setdefault("category", product_spec.get("category", "ebook"))
        metadata.setdefault("tags", product_spec.get("tags", []))
        metadata.setdefault("price", product_spec.get("price_usd", 19.0))
        metadata.setdefault("price_usd", product_spec.get("price_usd", 19.0))
        metadata.setdefault("price_idr", product_spec.get("price_idr", 285000))
        metadata.setdefault("currency", "USD")
        metadata.setdefault("language", "en")
        metadata.setdefault("license", product_spec.get("license", "commercial"))
        
        return metadata
    
    def _validate_metadata(self, product_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate product metadata"""
        product_dir = self.output_dir / product_id
        result = self.validation_engine.validate(str(product_dir), metadata)
        
        if hasattr(result, 'errors'):
            errors = result.errors
            valid = result.valid
        else:
            valid = result.get("valid", False)
            errors = result.get("errors", [])
        
        return {
            "valid": valid,
            "errors": errors,
            "score": result.get("score", 0.0) if isinstance(result, dict) else result.score
        }
    
    def _generate_cover(self, product_id: str) -> str:
        """Generate cover image (placeholder since no cover module exists)"""
        product_dir = self.output_dir / product_id
        thumbnail_dir = product_dir / "thumbnail"
        thumbnail_dir.mkdir(exist_ok=True)
        
        # Create a simple placeholder cover image (1x1 transparent PNG)
        cover_path = thumbnail_dir / "cover.png"
        
        # Minimal valid PNG file (1x1 transparent pixel)
        png_data = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
            b'\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01'
            b'\x00\x00\x05\x00\x01\x0d\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        
        with open(cover_path, "wb") as f:
            f.write(png_data)
        
        logger.info(f"Cover image generated: {cover_path}")
        return str(cover_path)
    
    async def _publish_to_gumroad(self, product_id: str, metadata: Dict[str, Any], 
                                   package_path: str, cover_path: str) -> Dict[str, Any]:
        """Publish product to Gumroad"""
        try:
            # Connect to Gumroad
            connected = await self.gumroad_provider.connect()
            if not connected:
                logger.warning("Gumroad connection failed, using test mode")
            
            # Build payload for Gumroad
            payload = {
                "title": metadata.get("title", product_id),
                "description": metadata.get("long_description", metadata.get("description", "")),
                "price": metadata.get("price", 19.0),
                "currency": metadata.get("currency", "USD"),
                "tags": metadata.get("tags", []),
                "published": True,
                "file_url": None,
                "thumbnail_url": None
            }
            
            # Create listing
            listing_result = await self.gumroad_provider.create_listing(payload)
            if not listing_result.get("success"):
                return {
                    "success": False,
                    "status": "failed",
                    "error": listing_result.get("error", "Create listing failed")
                }
            
            marketplace_product_id = listing_result.get("product_id")
            marketplace_url = listing_result.get("url")
            
            # Upload product file (ZIP)
            upload_result = await self.gumroad_provider.upload_file(package_path, "product")
            if upload_result.get("success"):
                file_url = upload_result.get("file_url")
                # Update listing with file URL
                await self.gumroad_provider.update_listing(
                    marketplace_product_id,
                    {"file_url": file_url}
                )
            
            # Upload thumbnail/cover
            cover_result = await self.gumroad_provider.upload_thumbnail(cover_path)
            if cover_result.get("success"):
                thumbnail_url = cover_result.get("file_url")
                # Update listing with thumbnail URL
                await self.gumroad_provider.update_listing(
                    marketplace_product_id,
                    {"thumbnail_url": thumbnail_url}
                )
            
            # Publish
            publish_result = await self.gumroad_provider.publish(marketplace_product_id)
            if not publish_result.get("success"):
                return {
                    "success": False,
                    "status": "failed",
                    "marketplace_product_id": marketplace_product_id,
                    "product_url": marketplace_url,
                    "error": publish_result.get("error", "Publish failed")
                }
            
            logger.info(f"Published to Gumroad: {marketplace_url}")
            
            return {
                "success": True,
                "status": "published",
                "marketplace": "gumroad",
                "marketplace_product_id": marketplace_product_id,
                "product_url": marketplace_url,
                "publish_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Gumroad publish failed: {e}")
            return {
                "success": False,
                "status": "failed",
                "error": str(e)
            }
    
    def _save_publication_record(self, product_id: str, publish_result: Dict[str, Any]):
        """Save publication record to database"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Create publications table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS publications (
                    id TEXT PRIMARY KEY,
                    product_id TEXT NOT NULL,
                    marketplace TEXT NOT NULL,
                    marketplace_product_id TEXT,
                    product_url TEXT,
                    publish_time TEXT NOT NULL,
                    publish_status TEXT NOT NULL,
                    data TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            
            publication_id = f"pub-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
            
            cursor.execute("""
                INSERT INTO publications 
                (id, product_id, marketplace, marketplace_product_id, product_url, 
                 publish_time, publish_status, data, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                publication_id,
                product_id,
                publish_result.get("marketplace", "gumroad"),
                publish_result.get("marketplace_product_id"),
                publish_result.get("product_url"),
                publish_result.get("publish_time", datetime.now().isoformat()),
                publish_result.get("status", "unknown"),
                json.dumps(publish_result),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            logger.info(f"Publication record saved: {publication_id}")
            
        except Exception as e:
            logger.error(f"Failed to save publication record: {e}")
    
    def _record_analytics(self, product_id: str, publish_result: Dict[str, Any]):
        """Record publication in analytics"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Ensure transactions table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id TEXT PRIMARY KEY,
                    gateway TEXT NOT NULL,
                    customer_email TEXT,
                    customer_name TEXT,
                    amount REAL NOT NULL,
                    currency TEXT NOT NULL,
                    fee_amount REAL DEFAULT 0.0,
                    net_amount REAL NOT NULL,
                    product_id TEXT,
                    status TEXT DEFAULT 'pending',
                    payment_method TEXT,
                    created_at TEXT,
                    completed_at TEXT,
                    metadata TEXT
                )
            """)
            
            # Record publication event
            transaction_id = f"txn-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
            metadata = {
                "type": "publication",
                "product_id": product_id,
                "marketplace": publish_result.get("marketplace"),
                "marketplace_product_id": publish_result.get("marketplace_product_id"),
                "product_url": publish_result.get("product_url")
            }
            
            cursor.execute("""
                INSERT INTO transactions 
                (id, gateway, amount, currency, net_amount, product_id, status, 
                 payment_method, created_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                transaction_id,
                publish_result.get("marketplace", "gumroad"),
                0.0,  # No revenue yet, just publication
                "USD",
                0.0,
                product_id,
                "published",
                "gumroad",
                datetime.now().isoformat(),
                json.dumps(metadata)
            ))
            
            conn.commit()
            logger.info(f"Analytics recorded: {transaction_id}")
            
        except Exception as e:
            logger.error(f"Failed to record analytics: {e}")


def main():
    """Test the publishing pipeline"""
    from pathlib import Path
    
    config = ConfigManager(Path("config/engine.yaml"))
    db = DatabaseManager(Path(config.get("database.path")))
    
    pipeline = PublishingPipeline(config, db)
    
    # Test product specification
    product_spec = {
        "title": "Digital Marketing Mastery 2026",
        "description": "Complete guide to digital marketing in 2026",
        "short_description": "Master digital marketing with this comprehensive guide.",
        "long_description": "This comprehensive guide covers all aspects of digital marketing in 2026, including SEO, social media, content marketing, and paid advertising.",
        "category": "ebook",
        "tags": ["digital marketing", "SEO", "social media", "2026"],
        "price_usd": 19.0,
        "price_idr": 285000,
        "license": "commercial",
        "target_market": "global"
    }
    
    print("Running Publishing Pipeline...")
    print(f"Product: {product_spec['title']}")
    
    import asyncio
    result = asyncio.run(pipeline.run(product_spec))
    
    print(f"\nPipeline Result:")
    print(f"  Success: {result.get('success')}")
    print(f"  Product ID: {result.get('product_id')}")
    print(f"  Product URL: {result.get('product_url')}")
    print(f"  Publish Status: {result.get('publish_status')}")
    print(f"  Publish Time: {result.get('publish_time')}")
    
    if result.get("error"):
        print(f"  Error: {result['error']}")
    
    db.close()


if __name__ == "__main__":
    main()
