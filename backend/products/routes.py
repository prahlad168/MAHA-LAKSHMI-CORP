"""
MAHA LAKSHMI CORP - Products Routes
Product factory and management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import json
import logging
import uuid

from backend.db.connection import get_db, execute_query
from backend.shared.security import verify_jwt_token
from backend.shared.rate_limiter import rate_limit

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()


class ProductGenerationRequest(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str = Field(min_length=1, max_length=10_000)
    price: float = Field(default=0, ge=0)
    currency: str = Field(default="USD", pattern=r"^[A-Z]{3}$")
    category: Optional[str] = Field(default=None, max_length=80)
    tags: List[str] = Field(default_factory=list, max_length=20)
    content: Optional[str] = Field(default=None, max_length=50_000)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current authenticated user"""
    payload = verify_jwt_token(credentials.credentials)
    user = execute_query("SELECT * FROM users WHERE id = ?", (payload["user_id"],), fetch="one")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/", tags=["Products"])
async def get_products(
    limit: int = 50,
    offset: int = 0,
    current_user: Dict = Depends(get_current_user)
):
    """Get all products"""
    try:
        products = execute_query(
            """
            SELECT * FROM products
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
            fetch="all"
        )
        
        total = execute_query(
            "SELECT COUNT(*) as count FROM products",
            fetch="one"
        )
        
        return {
            "products": products or [],
            "total": total["count"] if total else 0,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Failed to fetch products: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch products")


@router.get("/{product_id}", tags=["Products"])
async def get_product(product_id: str, current_user: Dict = Depends(get_current_user)):
    """Get product by ID"""
    try:
        product = execute_query(
            "SELECT * FROM products WHERE id = ?",
            (product_id,),
            fetch="one"
        )
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch product: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch product")


@router.post("/generate", tags=["Products"])
@rate_limit(max_requests=10, window_seconds=3600)
async def generate_product(
    request: Request,
    product_data: ProductGenerationRequest,
    current_user: Dict = Depends(get_current_user)
):
    """Generate new product using AI"""
    try:
        # Create product generation job
        job_id = f"prod-{uuid.uuid4().hex}"
        now = datetime.now(timezone.utc).isoformat()
        
        execute_query(
            """
            INSERT INTO product_generation_jobs (id, product_data, status, created_by, created_at, updated_at)
            VALUES (?, ?, 'queued', ?, ?, ?)
            """,
            (job_id, product_data.model_dump_json(), current_user["id"], now, now),
            fetch="none"
        )
        
        return {
            "job_id": job_id,
            "status": "queued",
            "message": "Product generation queued"
        }
    except Exception as e:
        logger.error(f"Failed to generate product: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate product")


@router.get("/jobs/{job_id}", tags=["Products"])
async def get_generation_job(job_id: str, current_user: Dict = Depends(get_current_user)):
    """Return the caller's product-generation job, including its final product id."""
    job = execute_query(
        "SELECT id, status, result, error, created_at, started_at, completed_at FROM product_generation_jobs WHERE id = ? AND created_by = ?",
        (job_id, current_user["id"]), fetch="one",
    )
    if not job:
        raise HTTPException(status_code=404, detail="Generation job not found")
    job["result"] = json.loads(job["result"]) if job["result"] else None
    return job
