#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Product Factory API
REST endpoints for product factory operations.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from core.engine import ConfigManager, DatabaseManager
from product_factory.core.factory import ProductFactory, ProductStatus, ProductCategory
from product_factory.generators.engine import ProductGeneratorFactory
from product_factory.quality.engine import QualityEngine
from product_factory.versioning.manager import VersionManager
from product_factory.packaging.packager import ProductPackager

app = FastAPI(
    title="MAHA Sales Engine - Product Factory API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Initialize components
BASE_DIR = Path(__file__).parent.parent.parent.parent
CONFIG = ConfigManager(BASE_DIR / "config/engine.yaml")
DB = DatabaseManager(Path(CONFIG.get("database.path")))
OUTPUT_DIR = BASE_DIR / "product-factory" / "output"

factory = ProductFactory(DB, CONFIG)
generator_factory = ProductGeneratorFactory(OUTPUT_DIR)
quality_engine = QualityEngine(OUTPUT_DIR)
version_manager = VersionManager(OUTPUT_DIR, DB)
packager = ProductPackager(OUTPUT_DIR)


# ============ MODELS ============

class ProductCreate(BaseModel):
    title: str
    category: str
    description: str = ""
    price_usd: float = 0.0
    price_idr: float = 0.0
    tags: List[str] = []
    language: str = "en"
    target_market: str = "global"
    author: str = "MAHA LAKSHMI"
    license_type: str = "personal"


class ProductGenerate(BaseModel):
    product_id: str
    generator_type: str
    parameters: Dict[str, Any] = {}


# ============ ENDPOINTS ============

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "module": "product-factory",
        "output_dir": str(OUTPUT_DIR)
    }


@app.post("/api/v1/products")
async def create_product(product: ProductCreate):
    """Create a new product idea"""
    try:
        category = product.category.lower().replace(" ", "_")
        valid_categories = [e.value for e in ProductCategory]
        
        if category not in valid_categories:
            # Try to match partial
            for valid_cat in valid_categories:
                if valid_cat in category or category in valid_cat:
                    category = valid_cat
                    break
        
        product_id = factory.create_product(
            title=product.title,
            category=category,
            description=product.description,
            price_usd=product.price_usd,
            price_idr=product.price_idr,
            tags=product.tags,
            language=product.language,
            target_market=product.target_market,
            author=product.author,
            license_type=product.license_type
        )
        
        if not product_id:
            raise HTTPException(status_code=400, detail="Failed to create product")
        
        return {"product_id": product_id, "status": "created"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/products")
async def list_products(status: Optional[str] = None, category: Optional[str] = None, limit: int = 100):
    """List products with optional filters"""
    try:
        products = factory.list_products(status=status, category=category, limit=limit)
        return {"products": products, "count": len(products)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/products/{product_id}")
async def get_product(product_id: str):
    """Get product by ID"""
    product = factory.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.patch("/api/v1/products/{product_id}/status")
async def update_product_status(product_id: str, status: str):
    """Update product status"""
    valid_statuses = [e.value for e in ProductStatus]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    success = factory.update_product_status(product_id, status)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update status")
    
    return {"product_id": product_id, "status": status}


@app.post("/api/v1/products/generate")
async def generate_product(request: ProductGenerate):
    """Generate product package"""
    try:
        generator = generator_factory.get_generator(request.generator_type)
        if not generator:
            raise HTTPException(status_code=400, detail=f"Unsupported generator: {request.generator_type}")
        
        result = generator.generate(
            product_id=request.product_id,
            title=request.parameters.get("title", "Untitled Product"),
            description=request.parameters.get("description", ""),
            **request.parameters
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Update product status
        factory.update_product_status(request.product_id, ProductStatus.GENERATING.value)
        
        # Run quality check
        quality_report = quality_engine.run_quality_check(request.product_id)
        
        # Create version
        version_id = version_manager.create_version(
            request.product_id,
            OUTPUT_DIR / request.product_id,
            f"Generated {request.generator_type}"
        )
        
        # Update status based on quality
        if quality_report.get("passed", False):
            factory.update_product_status(request.product_id, ProductStatus.REVIEW.value)
        else:
            factory.update_product_status(request.product_id, ProductStatus.GENERATING.value)
        
        return {
            "product_id": request.product_id,
            "generator": request.generator_type,
            "result": result,
            "quality_passed": quality_report.get("passed", False),
            "quality_score": quality_report.get("overall_score", 0),
            "version_id": version_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/products/{product_id}/quality-check")
async def run_quality_check(product_id: str):
    """Run quality check on product"""
    report = quality_engine.run_quality_check(product_id)
    return report


@app.post("/api/v1/products/{product_id}/package")
async def package_product(product_id: str, format: str = "zip"):
    """Package product for distribution"""
    product_dir = OUTPUT_DIR / product_id
    if not product_dir.exists():
        raise HTTPException(status_code=404, detail="Product not found")
    
    if format == "zip":
        package_path = packager.create_zip_package(product_id, product_dir)
    elif format == "folder":
        package_path = packager.create_folder_export(product_id, product_dir)
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Use 'zip' or 'folder'")
    
    if not package_path:
        raise HTTPException(status_code=400, detail="Failed to create package")
    
    manifest = packager.create_manifest(product_id, product_dir, package_path)
    
    return {
        "product_id": product_id,
        "format": format,
        "package_path": package_path,
        "manifest": manifest
    }


@app.get("/api/v1/products/{product_id}/versions")
async def get_version_history(product_id: str):
    """Get version history for product"""
    versions = version_manager.get_version_history(product_id)
    return {"product_id": product_id, "versions": versions}


@app.post("/api/v1/products/{product_id}/rollback")
async def rollback_product(product_id: str, version_id: str):
    """Rollback product to specific version"""
    success = version_manager.rollback_version(product_id, version_id)
    if not success:
        raise HTTPException(status_code=400, detail="Rollback failed")
    return {"product_id": product_id, "rolled_back_to": version_id}


@app.get("/api/v1/generators")
async def list_generators():
    """List available generators"""
    return {
        "generators": generator_factory.get_supported_categories()
    }


@app.get("/api/v1/categories")
async def list_categories():
    """List product categories"""
    categories = [{"id": e.value, "name": e.value.replace("_", " ").title()} for e in ProductCategory]
    return {"categories": categories}


@app.get("/api/v1/stats")
async def get_stats():
    """Get product factory statistics"""
    stats = factory.get_stats()
    return stats


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
