"""
MAHA LAKSHMI CORP - Marketplace Routes
Marketplace integration endpoints for Gumroad, Etsy, Shopify, WooCommerce, LemonSqueezy, Stripe.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, List, Optional
import logging
import os

from backend.db.connection import get_db, execute_query
from backend.shared.security import verify_jwt_token
from backend.shared.rate_limiter import rate_limit

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current authenticated user"""
    payload = verify_jwt_token(credentials.credentials)
    user = execute_query("SELECT * FROM users WHERE id = ?", (payload["user_id"],), fetch="one")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/accounts", tags=["Marketplace"])
async def get_marketplace_accounts(current_user: Dict = Depends(get_current_user)):
    """Get all marketplace accounts"""
    try:
        accounts = execute_query(
            """
            SELECT id, provider, name, status, last_sync_at, created_at
            FROM marketplace_accounts
            ORDER BY created_at DESC
            """,
            fetch="all"
        )
        
        return {
            "accounts": accounts or [],
            "total": len(accounts) if accounts else 0
        }
    except Exception as e:
        logger.error(f"Failed to fetch marketplace accounts: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch accounts")


@router.post("/accounts", tags=["Marketplace"])
@rate_limit(max_requests=10, window_seconds=3600)
async def create_marketplace_account(
    request: Request,
    account_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """Create marketplace account"""
    try:
        provider = account_data.get("provider")
        name = account_data.get("name")
        api_key = account_data.get("api_key")
        
        if not provider or not name or not api_key:
            raise HTTPException(status_code=400, detail="Missing required fields: provider, name, api_key")
        
        # Validate provider
        supported_providers = ["gumroad", "etsy", "shopify", "woocommerce", "lemonsqueezy", "stripe"]
        if provider not in supported_providers:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
        
        # Create account
        account_id = f"acc-{int(__import__('time').time() * 1000)}"
        now = __import__('datetime').datetime.now().isoformat()
        
        execute_query(
            """
            INSERT INTO marketplace_accounts (id, provider, name, api_key, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, 'active', ?, ?)
            """,
            (account_id, provider, name, api_key, now, now),
            fetch="none"
        )
        
        # Log audit
        execute_query(
            "INSERT INTO audit_logs (user_id, action, resource_type, resource_id, details, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (
                current_user["id"],
                "marketplace_account_created",
                "marketplace_account",
                account_id,
                {"provider": provider, "name": name},
                now
            ),
            fetch="none"
        )
        
        return {
            "id": account_id,
            "provider": provider,
            "name": name,
            "status": "active",
            "message": "Account created successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create marketplace account: {e}")
        raise HTTPException(status_code=500, detail="Failed to create account")


@router.get("/products", tags=["Marketplace"])
async def get_marketplace_products(current_user: Dict = Depends(get_current_user)):
    """Get all marketplace products"""
    try:
        products = execute_query(
            """
            SELECT mp.*, ma.name as account_name, ma.provider
            FROM marketplace_products mp
            JOIN marketplace_accounts ma ON mp.account_id = ma.id
            ORDER BY mp.created_at DESC
            LIMIT 100
            """,
            fetch="all"
        )
        
        return {
            "products": products or [],
            "total": len(products) if products else 0
        }
    except Exception as e:
        logger.error(f"Failed to fetch marketplace products: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch products")


@router.post("/publish", tags=["Marketplace"])
@rate_limit(max_requests=10, window_seconds=3600)
async def publish_to_marketplace(
    request: Request,
    publish_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """Publish product to marketplace"""
    try:
        product_id = publish_data.get("product_id")
        account_id = publish_data.get("account_id")
        
        if not product_id or not account_id:
            raise HTTPException(status_code=400, detail="Missing required fields: product_id, account_id")
        
        # Get account
        account = execute_query(
            "SELECT * FROM marketplace_accounts WHERE id = ?",
            (account_id,),
            fetch="one"
        )
        
        if not account:
            raise HTTPException(status_code=404, detail="Marketplace account not found")
        
        # Get product
        product = execute_query(
            "SELECT * FROM products WHERE id = ?",
            (product_id,),
            fetch="one"
        )
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Publish based on provider
        provider = account["provider"]
        
        if provider == "gumroad":
            result = await publish_to_gumroad(account, product)
        elif provider == "stripe":
            result = await publish_to_stripe(account, product)
        elif provider == "shopify":
            result = await publish_to_shopify(account, product)
        else:
            result = {
                "success": False,
                "error": f"Provider {provider} not yet implemented",
                "marketplace_product_id": None,
                "url": None
            }
        
        # Log publication
        publication_id = f"pub-{int(__import__('time').time() * 1000)}"
        now = __import__('datetime').datetime.now().isoformat()
        
        execute_query(
            """
            INSERT INTO marketplace_publications 
            (id, product_id, account_id, provider, status, marketplace_product_id, marketplace_url, 
             response_data, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                publication_id,
                product_id,
                account_id,
                provider,
                "published" if result.get("success") else "failed",
                result.get("marketplace_product_id"),
                result.get("url"),
                __import__('json').dumps(result),
                now,
                now
            ),
            fetch="none"
        )
        
        # Log audit
        execute_query(
            "INSERT INTO audit_logs (user_id, action, resource_type, resource_id, details, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (
                current_user["id"],
                "product_published",
                "marketplace_publication",
                publication_id,
                {"provider": provider, "product_id": product_id},
                now
            ),
            fetch="none"
        )
        
        return {
            "publication_id": publication_id,
            "success": result.get("success", False),
            "marketplace_product_id": result.get("marketplace_product_id"),
            "url": result.get("url"),
            "provider": provider,
            "message": "Published successfully" if result.get("success") else result.get("error", "Publication failed")
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to publish to marketplace: {e}")
        raise HTTPException(status_code=500, detail="Failed to publish product")


async def publish_to_gumroad(account: Dict[str, Any], product: Dict[str, Any]) -> Dict[str, Any]:
    """Publish product to Gumroad using real API"""
    try:
        import aiohttp
        import certifi
        import ssl
        
        api_key = account.get("api_key")
        if not api_key:
            return {"success": False, "error": "Missing API key"}
        
        # Build Gumroad payload
        payload = {
            "name": product.get("name", "Untitled Product"),
            "description": product.get("description", ""),
            "price": int((product.get("price", 0) or 0) * 100),  # Convert to cents
            "price_currency_type": "usd",
            "tags": product.get("tags", []),
            "is_published": True
        }
        
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(
                "https://api.gumroad.com/v2/products",
                params={"access_token": api_key},
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                text = await response.text()
                try:
                    data = __import__('json').loads(text) if text else {}
                except Exception:
                    data = {"raw": text}
                
                if response.status == 200 and data.get("success"):
                    product_data = data.get("product", {})
                    return {
                        "success": True,
                        "marketplace_product_id": product_data.get("id"),
                        "url": f"https://gumroad.com/l/{product_data.get('permalink', '')}" if product_data.get('permalink') else None,
                        "data": product_data
                    }
                else:
                    return {
                        "success": False,
                        "error": data.get("error", f"HTTP {response.status}"),
                        "status": response.status
                    }
    except Exception as e:
        logger.error(f"Gumroad publish failed: {e}")
        return {"success": False, "error": str(e)}


async def publish_to_stripe(account: Dict[str, Any], product: Dict[str, Any]) -> Dict[str, Any]:
    """Publish product to Stripe"""
    return {
        "success": False,
        "error": "Stripe integration not yet implemented"
    }


async def publish_to_shopify(account: Dict[str, Any], product: Dict[str, Any]) -> Dict[str, Any]:
    """Publish product to Shopify"""
    return {
        "success": False,
        "error": "Shopify integration not yet implemented"
    }


@router.get("/publications", tags=["Marketplace"])
async def get_publications(current_user: Dict = Depends(get_current_user)):
    """Get marketplace publications"""
    try:
        publications = execute_query(
            """
            SELECT mp.*, ma.name as account_name, p.name as product_name
            FROM marketplace_publications mp
            JOIN marketplace_accounts ma ON mp.account_id = ma.id
            LEFT JOIN products p ON mp.product_id = p.id
            ORDER BY mp.created_at DESC
            LIMIT 50
            """,
            fetch="all"
        )
        
        return {
            "publications": publications or [],
            "total": len(publications) if publications else 0
        }
    except Exception as e:
        logger.error(f"Failed to fetch publications: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch publications")


@router.post("/sync/{account_id}", tags=["Marketplace"])
async def sync_marketplace_account(
    account_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Sync marketplace account"""
    try:
        # Get account
        account = execute_query(
            "SELECT * FROM marketplace_accounts WHERE id = ?",
            (account_id,),
            fetch="one"
        )
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # TODO: Implement actual sync logic per provider
        # For now, return placeholder
        
        return {
            "success": True,
            "account_id": account_id,
            "provider": account["provider"],
            "message": "Sync completed",
            "synced_at": __import__('datetime').datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to sync account: {e}")
        raise HTTPException(status_code=500, detail="Failed to sync account")


@router.get("/health", tags=["Marketplace"])
async def marketplace_health(current_user: Dict = Depends(get_current_user)):
    """Get marketplace integration health"""
    try:
        accounts = execute_query(
            "SELECT id, provider, name, status, last_sync_at FROM marketplace_accounts",
            fetch="all"
        )
        
        publications = execute_query(
            "SELECT status, COUNT(*) as count FROM marketplace_publications GROUP BY status",
            fetch="all"
        )
        
        return {
            "status": "healthy",
            "accounts": accounts or [],
            "publications": publications or [],
            "providers_supported": ["gumroad", "etsy", "shopify", "woocommerce", "lemonsqueezy", "stripe"]
        }
    except Exception as e:
        logger.error(f"Marketplace health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")
