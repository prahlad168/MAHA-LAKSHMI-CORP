#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Gumroad Provider
Production-ready Gumroad marketplace provider implementation using Gumroad API v2.
"""

import os
import sys
import json
import time
import uuid
import logging
import aiohttp
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from marketplace_connector.core.marketplace_provider import MarketplaceProvider, ProviderType, PublicationStatus

logger = logging.getLogger("maha-sales-engine.marketplace_connector.gumroad")


class GumroadProvider(MarketplaceProvider):
    """
    Gumroad marketplace provider implementation.
    Uses Gumroad API v2: https://api.gumroad.com/v2/
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.provider_type = ProviderType.GUMROAD
        self.api_key = config.get("api_key") or os.getenv("GUMROAD_API_KEY", "")
        if not self.api_key:
            raise ValueError("GUMROAD_API_KEY is required for real Gumroad publishing")
        self.base_url = "https://api.gumroad.com/v2"
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def connect(self) -> bool:
        """Connect to Gumroad API"""
        try:
            self.session = aiohttp.ClientSession()
            result = await self.validate()
            return result.get("valid", False)
        except Exception as e:
            logger.error(f"Gumroad connection failed: {e}")
            return False
    
    async def validate(self) -> Dict[str, Any]:
        """Validate credentials"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(
                f"{self.base_url}/user",
                params={"access_token": self.api_key}
            ) as response:
                text = await response.text()
                if response.status == 200:
                    data = json.loads(text)
                    if data.get("success"):
                        return {"valid": True, "message": "Connection successful", "user": data.get("user")}
                    return {"valid": False, "error": data.get("error", "Invalid credentials")}
                else:
                    return {"valid": False, "error": f"HTTP {response.status}: {text}"}
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return {"valid": False, "error": str(e)}
    
    async def upload_file(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """Upload file to Gumroad using presigned S3 multipart flow"""
        try:
            if not os.path.exists(file_path):
                return {"success": False, "error": "File not found"}
            
            file_size = os.path.getsize(file_path)
            file_name = Path(file_path).name
            
            presign_resp = await self._request("POST", "/files/presign", json={
                "filename": file_name,
                "file_size": file_size
            })
            
            if not presign_resp.get("success"):
                return {"success": False, "error": presign_resp.get("error", "Presign failed")}
            
            presign_data = presign_resp.get("data", {})
            upload_id = presign_data.get("upload_id")
            key = presign_data.get("key")
            upload_urls = presign_data.get("presigned_urls", [])
            
            if not upload_urls:
                return {"success": False, "error": "No presigned URLs returned"}
            
            etags = []
            with open(file_path, "rb") as f:
                for idx, part in enumerate(upload_urls):
                    chunk = f.read(min(len(part.get("url", "")), 100 * 1024 * 1024))
                    async with self.session.put(
                        part["url"],
                        data=chunk,
                        headers={"Content-Type": "application/octet-stream"}
                    ) as resp:
                        if resp.status in (200, 201):
                            etag = resp.headers.get("ETag")
                            if etag:
                                etags.append({"part_number": idx + 1, "etag": etag})
            
            if not etags:
                return {"success": False, "error": "Upload produced no ETags"}
            
            complete_resp = await self._request("POST", "/files/complete", json={
                "upload_id": upload_id,
                "key": key,
                "parts": etags
            })
            
            if not complete_resp.get("success"):
                return {"success": False, "error": complete_resp.get("error", "Complete failed")}
            
            file_url = complete_resp.get("data", {}).get("file_url") or presign_data.get("file_url")
            return {"success": True, "file_url": file_url, "file_type": file_type}
        except Exception as e:
            logger.error(f"File upload failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def upload_thumbnail(self, file_path: str) -> Dict[str, Any]:
        """Upload thumbnail to Gumroad"""
        return await self.upload_file(file_path, "thumbnail")
    
    async def create_listing(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create Gumroad product listing"""
        try:
            gumroad_payload = self._build_gumroad_payload(payload)
            
            resp = await self._request("POST", "/products", json=gumroad_payload)
            if not resp.get("success"):
                return {"success": False, "error": resp.get("error", "Create listing failed")}
            
            product = resp.get("data", {}).get("product", {})
            product_id = product.get("id")
            permalink = product.get("permalink")
            url = f"https://gumroad.com/l/{permalink}" if permalink else None
            
            if not url:
                return {"success": False, "error": "Gumroad API did not return a permalink"}
            
            return {
                "success": True,
                "product_id": product_id,
                "url": url,
                "data": product
            }
        except Exception as e:
            logger.error(f"Create listing failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def update_listing(self, marketplace_product_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing listing"""
        try:
            gumroad_payload = self._build_gumroad_payload(payload)
            resp = await self._request("PUT", f"/products/{marketplace_product_id}", json=gumroad_payload)
            
            if not resp.get("success"):
                return {"success": False, "error": resp.get("error", "Update failed")}
            
            return {"success": True, "product_id": marketplace_product_id, "updated": True, "data": resp.get("data", {}).get("product")}
        except Exception as e:
            logger.error(f"Update listing failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def publish(self, marketplace_product_id: str) -> Dict[str, Any]:
        """Publish listing"""
        try:
            resp = await self._request("PUT", f"/products/{marketplace_product_id}/enable")
            if not resp.get("success"):
                return {"success": False, "error": resp.get("error", "Publish failed")}
            
            return {"success": True, "product_id": marketplace_product_id, "status": "published", "data": resp.get("data", {}).get("product")}
        except Exception as e:
            logger.error(f"Publish failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def archive(self, marketplace_product_id: str) -> Dict[str, Any]:
        """Archive listing"""
        try:
            resp = await self._request("PUT", f"/products/{marketplace_product_id}/disable")
            if not resp.get("success"):
                return {"success": False, "error": resp.get("error", "Archive failed")}
            
            return {"success": True, "product_id": marketplace_product_id, "status": "archived"}
        except Exception as e:
            logger.error(f"Archive failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def delete(self, marketplace_product_id: str) -> Dict[str, Any]:
        """Delete listing"""
        try:
            resp = await self._request("DELETE", f"/products/{marketplace_product_id}")
            if not resp.get("success"):
                return {"success": False, "error": resp.get("error", "Delete failed")}
            
            return {"success": True, "product_id": marketplace_product_id, "deleted": True}
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def sync(self, product_id: Optional[str] = None) -> Dict[str, Any]:
        """Sync product data"""
        try:
            if product_id:
                resp = await self._request("GET", f"/products/{product_id}")
                if not resp.get("success"):
                    return {"success": False, "error": resp.get("error", "Sync failed")}
                return {"success": True, "product": resp.get("product"), "timestamp": datetime.now().isoformat()}
            
            resp = await self._request("GET", "/products")
            products = []
            if resp.get("success"):
                products = [p.get("id") for p in resp.get("products", [])]
            return {"success": True, "synced_count": len(products), "timestamp": datetime.now().isoformat()}
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def health(self) -> Dict[str, Any]:
        """Check provider health"""
        try:
            validation = await self.validate()
            status = "healthy" if validation.get("valid") else "unhealthy"
            return {
                "status": status,
                "provider": "gumroad",
                "connected": validation.get("valid", False),
                "last_check": datetime.now().isoformat(),
                "details": validation
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": "gumroad",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
    
    def _build_gumroad_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Build Gumroad-specific payload"""
        price = payload.get("price")
        currency = payload.get("currency", "USD")
        price_cents = None
        price_currency_type = currency.lower()
        
        if isinstance(price, (int, float)):
            price_cents = int(round(float(price) * 100))
        
        return {
            "name": payload.get("title", ""),
            "description": payload.get("description", ""),
            "price": price_cents,
            "price_currency_type": price_currency_type,
            "tags": payload.get("tags", []),
            "is_published": payload.get("published", True),
            "file_url": payload.get("file_url"),
            "thumbnail_url": payload.get("thumbnail_url")
        }
    
    async def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        """Make authenticated request to Gumroad API"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        url = f"{self.base_url}{path}"
        params = kwargs.pop("params", {})
        params.setdefault("access_token", self.api_key)
        
        try:
            async with self.session.request(method, url, params=params, **kwargs) as response:
                text = await response.text()
                try:
                    data = json.loads(text) if text else {}
                except json.JSONDecodeError:
                    data = {"raw": text}
                
                if response.status >= 400:
                    return {
                        "success": False,
                        "error": data.get("error", f"HTTP {response.status}"),
                        "status": response.status,
                        "data": data
                    }
                
                return {"success": True, "data": data, "status": response.status}
        except Exception as e:
            logger.error(f"Gumroad request failed: {method} {path} - {e}")
            return {"success": False, "error": str(e)}
    
    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()


def main():
    print("Gumroad Provider loaded")


if __name__ == "__main__":
    main()
