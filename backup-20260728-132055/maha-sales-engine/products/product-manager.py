#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Product Manager
Responsibilities:
- Manage digital products
- Categories
- Pricing
- Versions
- Media
- Status
"""

import os
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

logger = logging.getLogger("maha-sales-engine.products")


class ProductStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class ProductCategory(Enum):
    SOCIAL_MEDIA = "social_media"
    SEO = "seo"
    WHATSAPP = "whatsapp"
    LANDING_PAGE = "landing_page"
    BUSINESS = "business"
    EDUCATION = "education"
    TEMPLATE = "template"


@dataclass
class Product:
    """Digital product definition"""
    id: str
    name: str
    description: str
    price_usd: float
    price_idr: float
    category: str
    features: List[str]
    status: str = ProductStatus.ACTIVE.value
    media_files: List[str] = field(default_factory=list)
    versions: List[Dict[str, Any]] = field(default_factory=list)
    marketplace_listings: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


class ProductManager:
    """Manage digital products"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.products: Dict[str, Product] = {}
        self.load_products()
    
    def load_products(self):
        """Load products from database"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE status = 'active'")
            rows = cursor.fetchall()
            
            for row in rows:
                product = Product(
                    id=row["id"],
                    name=row["name"],
                    description=row["description"],
                    price_usd=row["price_usd"],
                    price_idr=row["price_idr"],
                    category=row["category"],
                    features=json.loads(row["features"]),
                    status=row["status"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"]
                )
                self.products[product.id] = product
            
            logger.info(f"Loaded {len(self.products)} products")
            
        except Exception as e:
            logger.error(f"Failed to load products: {e}")
    
    def create_product(self, product: Product) -> bool:
        """Create a new product"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO products (id, name, description, price_usd, price_idr, category, features, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product.id,
                product.name,
                product.description,
                product.price_usd,
                product.price_idr,
                product.category,
                json.dumps(product.features),
                product.status,
                product.created_at,
                product.updated_at
            ))
            
            conn.commit()
            self.products[product.id] = product
            
            logger.info(f"Product created: {product.id} - {product.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create product: {e}")
            return False
    
    def update_product(self, product_id: str, updates: Dict[str, Any]) -> bool:
        """Update product"""
        try:
            if product_id not in self.products:
                return False
            
            product = self.products[product_id]
            
            # Update fields
            for key, value in updates.items():
                if hasattr(product, key):
                    setattr(product, key, value)
            
            product.updated_at = datetime.now().isoformat()
            
            # Update database
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE products 
                SET name = ?, description = ?, price_usd = ?, price_idr = ?, 
                    category = ?, features = ?, status = ?, updated_at = ?
                WHERE id = ?
            """, (
                product.name,
                product.description,
                product.price_usd,
                product.price_idr,
                product.category,
                json.dumps(product.features),
                product.status,
                product.updated_at,
                product_id
            ))
            
            conn.commit()
            logger.info(f"Product updated: {product_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update product: {e}")
            return False
    
    def get_product(self, product_id: str) -> Optional[Product]:
        """Get product by ID"""
        return self.products.get(product_id)
    
    def get_products_by_category(self, category: str) -> List[Product]:
        """Get products by category"""
        return [p for p in self.products.values() if p.category == category]
    
    def get_active_products(self) -> List[Product]:
        """Get all active products"""
        return [p for p in self.products.values() if p.status == ProductStatus.ACTIVE.value]
    
    def archive_product(self, product_id: str) -> bool:
        """Archive a product"""
        return self.update_product(product_id, {"status": ProductStatus.ARCHIVED.value})
    
    def add_marketplace_listing(self, product_id: str, marketplace: str, listing_data: Dict[str, Any]):
        """Add marketplace listing for product"""
        if product_id in self.products:
            self.products[product_id].marketplace_listings[marketplace] = listing_data
            logger.info(f"Marketplace listing added: {product_id} -> {marketplace}")
    
    def get_marketplace_listings(self, product_id: str) -> Dict[str, Dict[str, Any]]:
        """Get all marketplace listings for product"""
        if product_id in self.products:
            return self.products[product_id].marketplace_listings
        return {}
    
    def get_all_products(self) -> List[Dict[str, Any]]:
        """Get all products as dictionaries"""
        return [asdict(p) for p in self.products.values()]
    
    def initialize_default_products(self):
        """Initialize default products if none exist"""
        if self.products:
            return
        
        default_products = [
            Product(
                id="social-media-kit",
                name="Social Media Kit Pro",
                description="500+ templates for Instagram, Facebook, TikTok, LinkedIn, YouTube",
                price_usd=19.00,
                price_idr=285000,
                category=ProductCategory.SOCIAL_MEDIA.value,
                features=["instagram", "facebook", "tiktok", "linkedin", "youtube", "canva"],
                status=ProductStatus.ACTIVE.value
            ),
            Product(
                id="seo-bundle",
                name="SEO Master Bundle",
                description="50+ templates, checklists, and Notion workspace for SEO",
                price_usd=39.00,
                price_idr=585000,
                category=ProductCategory.SEO.value,
                features=["templates", "notion", "checklists", "analytics"],
                status=ProductStatus.ACTIVE.value
            ),
            Product(
                id="whatsapp-marketing",
                name="WhatsApp Marketing Kit",
                description="100+ message templates and automation scripts",
                price_usd=29.00,
                price_idr=435000,
                category=ProductCategory.WHATSAPP.value,
                features=["templates", "automation", "scripts", "bulk-sender"],
                status=ProductStatus.ACTIVE.value
            ),
            Product(
                id="landing-template",
                name="High-Converting Landing Page Template",
                description="5 professionally designed landing pages optimized for conversion",
                price_usd=49.00,
                price_idr=735000,
                category=ProductCategory.LANDING_PAGE.value,
                features=["html", "css", "figma", "responsive", "ab-tested"],
                status=ProductStatus.ACTIVE.value
            ),
            Product(
                id="business-kit",
                name="Complete Business Kit",
                description="All 4 products + 2 bonuses for complete business automation",
                price_usd=99.00,
                price_idr=1485000,
                category=ProductCategory.BUSINESS.value,
                features=["all-products", "bonus-templates", "commercial-license"],
                status=ProductStatus.ACTIVE.value
            )
        ]
        
        for product in default_products:
            self.create_product(product)
        
        logger.info(f"Initialized {len(default_products)} default products")


def main():
    """Test product manager"""
    from core.engine import DatabaseManager
    from pathlib import Path
    
    db = DatabaseManager(Path("db/maha_sales_engine.db"))
    pm = ProductManager(db)
    
    # Initialize defaults
    pm.initialize_default_products()
    
    # List products
    print("\nActive Products:")
    for product in pm.get_active_products():
        print(f"  - {product.name}: ${product.price_usd}")
    
    db.close()


if __name__ == "__main__":
    main()
