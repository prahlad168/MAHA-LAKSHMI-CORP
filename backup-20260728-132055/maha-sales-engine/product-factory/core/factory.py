#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - AI Product Factory
Autonomous Digital Product Generation Pipeline

Responsibilities:
- Generate digital products from ideas
- Version control with rollback
- Quality assurance
- Packaging and export
- License management
"""

import os
import sys
import json
import time
import uuid
import hashlib
import logging
import zipfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field
from enum import Enum
import sqlite3

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.engine import DatabaseManager, ConfigManager

logger = logging.getLogger("maha-sales-engine.product-factory")

# ============ CONFIGURATION ============

BASE_DIR = Path(__file__).parent.parent.parent
PRODUCT_FACTORY_DIR = BASE_DIR / "product-factory"
OUTPUT_DIR = PRODUCT_FACTORY_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ============ ENUMS ============

class ProductStatus(Enum):
    IDEA = "idea"
    GENERATING = "generating"
    REVIEW = "review"
    APPROVED = "approved"
    PACKAGED = "packaged"
    ARCHIVED = "archived"

class ProductCategory(Enum):
    EBOOK = "ebook"
    PROMPT_PACK = "prompt_pack"
    AI_SYSTEM_PROMPT = "ai_system_prompt"
    CHECKLIST = "checklist"
    TEMPLATE = "template"
    BUSINESS_DOCUMENT = "business_document"
    SOP_PACKAGE = "sop_package"
    NOTION_TEMPLATE = "notion_template"
    EXCEL_TEMPLATE = "excel_template"
    CANVA_ASSET_PACK = "canva_asset_pack"
    SVG_ICON_PACK = "svg_icon_pack"
    SOCIAL_MEDIA_CONTENT_PACK = "social_media_content_pack"
    PRINTABLE_PRODUCT = "printable_product"
    MINI_COURSE = "mini_course"
    SOURCE_CODE_TEMPLATE = "source_code_template"
    DOCUMENTATION_PACK = "documentation_pack"

class LicenseType(Enum):
    COMMERCIAL = "commercial"
    PERSONAL = "personal"
    EXTENDED = "extended"
    CUSTOM = "custom"

class GenerationJobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# ============ DATA MODELS ============

@dataclass
class ProductVersion:
    """Product version information"""
    version_id: str
    product_id: str
    version_number: str
    created_at: str
    created_by: str
    changelog: str
    file_path: str
    file_hash: str
    file_size: int
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class QualityReport:
    """Quality check report"""
    report_id: str
    product_id: str
    version_id: str
    created_at: str
    overall_score: float
    checks: List[Dict[str, Any]]
    passed: bool
    issues: List[str]

@dataclass
class GenerationJob:
    """Product generation job"""
    job_id: str
    product_id: str
    status: str
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    generator_type: str
    parameters: Dict[str, Any]
    result_path: Optional[str]
    error_message: Optional[str]
    logs: List[str] = field(default_factory=list)

# ============ PRODUCT FACTORY CORE ============

class ProductFactory:
    """Main product factory orchestrator"""
    
    def __init__(self, db_manager: DatabaseManager, config: ConfigManager):
        self.db = db_manager
        self.config = config
        self.output_dir = OUTPUT_DIR
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize database tables
        self._init_database()
        
        logger.info("Product Factory initialized")
    
    def _init_database(self):
        """Initialize product factory tables"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pf_products (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT NOT NULL,
                status TEXT DEFAULT 'idea',
                license_type TEXT DEFAULT 'personal',
                price_usd REAL DEFAULT 0.0,
                price_idr REAL DEFAULT 0.0,
                author TEXT DEFAULT 'MAHA LAKSHMI',
                tags TEXT,
                target_market TEXT,
                language TEXT DEFAULT 'en',
                file_path TEXT,
                preview_path TEXT,
                thumbnail_path TEXT,
                version_count INTEGER DEFAULT 0,
                download_count INTEGER DEFAULT 0,
                rating REAL DEFAULT 0.0,
                review_count INTEGER DEFAULT 0,
                created_at TEXT,
                updated_at TEXT,
                archived_at TEXT
            )
        """)
        
        # Product versions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pf_product_versions (
                id TEXT PRIMARY KEY,
                product_id TEXT NOT NULL,
                version_number TEXT NOT NULL,
                created_at TEXT,
                created_by TEXT,
                changelog TEXT,
                file_path TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                file_size INTEGER,
                metadata TEXT,
                FOREIGN KEY (product_id) REFERENCES pf_products (id)
            )
        """)
        
        # Product categories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pf_product_categories (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                icon TEXT,
                created_at TEXT
            )
        """)
        
        # Product keywords table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pf_product_keywords (
                id TEXT PRIMARY KEY,
                product_id TEXT NOT NULL,
                keyword TEXT NOT NULL,
                language TEXT DEFAULT 'en',
                search_volume INTEGER DEFAULT 0,
                competition TEXT DEFAULT 'medium',
                created_at TEXT,
                FOREIGN KEY (product_id) REFERENCES pf_products (id)
            )
        """)
        
        # Licenses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pf_licenses (
                id TEXT PRIMARY KEY,
                product_id TEXT NOT NULL,
                license_type TEXT NOT NULL,
                terms TEXT,
                restrictions TEXT,
                created_at TEXT,
                FOREIGN KEY (product_id) REFERENCES pf_products (id)
            )
        """)
        
        # Quality reports table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pf_quality_reports (
                id TEXT PRIMARY KEY,
                product_id TEXT NOT NULL,
                version_id TEXT NOT NULL,
                created_at TEXT,
                overall_score REAL,
                checks TEXT NOT NULL,
                passed BOOLEAN DEFAULT 0,
                issues TEXT,
                FOREIGN KEY (product_id) REFERENCES pf_products (id),
                FOREIGN KEY (version_id) REFERENCES pf_product_versions (id)
            )
        """)
        
        # Generation jobs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pf_generation_jobs (
                id TEXT PRIMARY KEY,
                product_id TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT,
                started_at TEXT,
                completed_at TEXT,
                generator_type TEXT,
                parameters TEXT,
                result_path TEXT,
                error_message TEXT,
                logs TEXT,
                FOREIGN KEY (product_id) REFERENCES pf_products (id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pf_products_status ON pf_products(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pf_products_category ON pf_products(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pf_products_created ON pf_products(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pf_versions_product ON pf_product_versions(product_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pf_keywords_product ON pf_product_keywords(product_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pf_jobs_status ON pf_generation_jobs(status)")
        
        conn.commit()
        logger.info("Product Factory database tables initialized")
    
    def _generate_product_id(self) -> str:
        """Generate globally unique product ID"""
        timestamp = datetime.now().strftime("%Y%m%d")
        sequence = hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:6].upper()
        return f"ML-{timestamp}-{sequence}"
    
    def create_product(self, title: str, category: str, description: str = "", **kwargs) -> Optional[str]:
        """Create a new product idea"""
        try:
            product_id = self._generate_product_id()
            
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO pf_products (
                    id, title, description, category, status,
                    license_type, price_usd, price_idr, author, tags,
                    target_market, language, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_id,
                title,
                description,
                category,
                ProductStatus.IDEA.value,
                kwargs.get("license_type", LicenseType.PERSONAL.value),
                kwargs.get("price_usd", 0.0),
                kwargs.get("price_idr", 0.0),
                kwargs.get("author", "MAHA LAKSHMI"),
                json.dumps(kwargs.get("tags", [])),
                kwargs.get("target_market", "global"),
                kwargs.get("language", "en"),
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            logger.info(f"Product created: {product_id} - {title}")
            
            return product_id
            
        except Exception as e:
            logger.error(f"Failed to create product: {e}")
            return None
    
    def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get product by ID"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pf_products WHERE id = ?", (product_id,))
            row = cursor.fetchone()
            
            if row:
                product = dict(row)
                product["tags"] = json.loads(product.get("tags", "[]"))
                return product
            return None
            
        except Exception as e:
            logger.error(f"Failed to get product: {e}")
            return None
    
    def list_products(self, status: Optional[str] = None, category: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """List products with optional filters"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM pf_products"
            params = []
            
            if status:
                query += " WHERE status = ?"
                params.append(status)
            elif category:
                query += " WHERE category = ?"
                params.append(category)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            products = []
            for row in rows:
                product = dict(row)
                product["tags"] = json.loads(product.get("tags", "[]"))
                products.append(product)
            
            return products
            
        except Exception as e:
            logger.error(f"Failed to list products: {e}")
            return []
    
    def update_product_status(self, product_id: str, status: str) -> bool:
        """Update product status"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            updates = {
                "status": status,
                "updated_at": datetime.now().isoformat()
            }
            
            if status == ProductStatus.ARCHIVED.value:
                updates["archived_at"] = datetime.now().isoformat()
            
            set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values()) + [product_id]
            
            cursor.execute(f"UPDATE pf_products SET {set_clause} WHERE id = ?", values)
            conn.commit()
            
            logger.info(f"Product status updated: {product_id} -> {status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update product status: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get product factory statistics"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Total products
            cursor.execute("SELECT COUNT(*) FROM pf_products")
            total_products = cursor.fetchone()[0]
            
            # Products by status
            cursor.execute("SELECT status, COUNT(*) FROM pf_products GROUP BY status")
            by_status = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Products by category
            cursor.execute("SELECT category, COUNT(*) FROM pf_products GROUP BY category")
            by_category = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Generation jobs
            cursor.execute("SELECT COUNT(*) FROM pf_generation_jobs")
            total_jobs = cursor.fetchone()[0]
            
            cursor.execute("SELECT status, COUNT(*) FROM pf_generation_jobs GROUP BY status")
            jobs_by_status = {row[0]: row[1] for row in cursor.fetchall()}
            
            return {
                "total_products": total_products,
                "by_status": by_status,
                "by_category": by_category,
                "total_jobs": total_jobs,
                "jobs_by_status": jobs_by_status,
                "success_rate": (jobs_by_status.get("completed", 0) / total_jobs * 100) if total_jobs > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}
    
    def get_status(self) -> Dict[str, Any]:
        """Get module status"""
        stats = self.get_stats()
        return {
            "module": "product-factory",
            "status": "running",
            "stats": stats,
            "output_dir": str(self.output_dir)
        }


def main():
    """Test product factory"""
    from core.engine import ConfigManager, DatabaseManager
    from pathlib import Path
    
    config = ConfigManager(Path("config/engine.yaml"))
    db = DatabaseManager(Path(config.get("database.path")))
    
    factory = ProductFactory(db, config)
    
    # Test creating a product
    product_id = factory.create_product(
        title="Social Media Kit Pro",
        category=ProductCategory.SOCIAL_MEDIA_CONTENT_PACK.value,
        description="500+ social media templates",
        price_usd=19.0,
        price_idr=285000,
        tags=["social media", "templates", "instagram"],
        target_market="global"
    )
    
    if product_id:
        print(f"✅ Product created: {product_id}")
        
        # Update status
        factory.update_product_status(product_id, ProductStatus.REVIEW.value)
        
        # Get stats
        stats = factory.get_stats()
        print(f"\nFactory Stats:")
        print(f"  Total Products: {stats['total_products']}")
        print(f"  By Status: {stats['by_status']}")
    
    db.close()


if __name__ == "__main__":
    main()
