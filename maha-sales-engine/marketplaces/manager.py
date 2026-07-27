#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Marketplace Manager
Responsibilities:
- Supported marketplace integrations
- Listing management
- Product synchronization
- Listing updates
- Publication status
"""

import json
import time
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

logger = logging.getLogger("maha-sales-engine.marketplaces")


class MarketplaceType(Enum):
    GUMROAD = "gumroad"
    SHOPIFY = "shopify"
    ETSY = "etsy"
    CREATIVE_MARKET = "creative_market"
    THEMEFOREST = "themeforest"
    G2 = "g2"


class ListingStatus(Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    PAUSED = "paused"
    ARCHIVED = "archived"
    PENDING_REVIEW = "pending_review"


@dataclass
class MarketplaceListing:
    """Marketplace listing"""
    listing_id: str
    product_id: str
    marketplace: str
    status: str
    url: Optional[str]
    price: float
    currency: str
    views: int = 0
    sales: int = 0
    reviews: int = 0
    rating: float = 0.0
    last_synced: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class MarketplaceManager:
    """Manage marketplace integrations"""
    
    def __init__(self, config, product_manager):
        self.config = config
        self.product_manager = product_manager
        self.listings: Dict[str, MarketplaceListing] = {}
        self.integrations: Dict[str, Any] = {}
    
    def register_integration(self, marketplace: MarketplaceType, credentials: Dict[str, Any]):
        """Register marketplace integration"""
        self.integrations[marketplace.value] = {
            "credentials": credentials,
            "enabled": True,
            "last_sync": None
        }
        logger.info(f"Integration registered: {marketplace.value}")
    
    def create_listing(self, product_id: str, marketplace: str, listing_data: Dict[str, Any]) -> Optional[str]:
        """Create product listing on marketplace"""
        try:
            listing_id = f"LST-{marketplace.upper()}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            listing = MarketplaceListing(
                listing_id=listing_id,
                product_id=product_id,
                marketplace=marketplace,
                status=ListingStatus.DRAFT.value,
                url=None,
                price=listing_data.get("price", 0.0),
                currency=listing_data.get("currency", "USD")
            )
            
            self.listings[listing_id] = listing
            
            # In production: call marketplace API to create listing
            logger.info(f"Listing created: {listing_id} for {product_id} on {marketplace}")
            
            return listing_id
            
        except Exception as e:
            logger.error(f"Failed to create listing: {e}")
            return None
    
    def publish_listing(self, listing_id: str) -> bool:
        """Publish listing on marketplace"""
        try:
            if listing_id not in self.listings:
                return False
            
            listing = self.listings[listing_id]
            listing.status = ListingStatus.PUBLISHED.value
            
            # In production: call marketplace API to publish
            logger.info(f"Listing published: {listing_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish listing: {e}")
            return False
    
    def update_listing(self, listing_id: str, updates: Dict[str, Any]) -> bool:
        """Update marketplace listing"""
        try:
            if listing_id not in self.listings:
                return False
            
            listing = self.listings[listing_id]
            
            # Update fields
            for key, value in updates.items():
                if hasattr(listing, key):
                    setattr(listing, key, value)
            
            listing.last_synced = datetime.now().isoformat()
            
            # In production: call marketplace API to update
            logger.info(f"Listing updated: {listing_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update listing: {e}")
            return False
    
    def sync_listing(self, listing_id: str) -> Dict[str, Any]:
        """Sync listing data from marketplace"""
        try:
            if listing_id not in self.listings:
                return {}
            
            listing = self.listings[listing_id]
            
            # In production: call marketplace API to get latest data
            # For now, return placeholder
            sync_data = {
                "listing_id": listing_id,
                "views": listing.views,
                "sales": listing.sales,
                "reviews": listing.reviews,
                "rating": listing.rating,
                "synced_at": datetime.now().isoformat()
            }
            
            listing.last_synced = datetime.now().isoformat()
            return sync_data
            
        except Exception as e:
            logger.error(f"Failed to sync listing: {e}")
            return {}
    
    def get_listing(self, listing_id: str) -> Optional[Dict[str, Any]]:
        """Get listing by ID"""
        if listing_id in self.listings:
            return asdict(self.listings[listing_id])
        return None
    
    def get_listings_by_product(self, product_id: str) -> List[Dict[str, Any]]:
        """Get all listings for a product"""
        return [
            asdict(listing) for listing in self.listings.values()
            if listing.product_id == product_id
        ]
    
    def get_listings_by_marketplace(self, marketplace: str) -> List[Dict[str, Any]]:
        """Get all listings for a marketplace"""
        return [
            asdict(listing) for listing in self.listings.values()
            if listing.marketplace == marketplace
        ]
    
    def get_published_listings(self) -> List[Dict[str, Any]]:
        """Get all published listings"""
        return [
            asdict(listing) for listing in self.listings.values()
            if listing.status == ListingStatus.PUBLISHED.value
        ]
    
    def get_listing_stats(self) -> Dict[str, Any]:
        """Get listing statistics"""
        total = len(self.listings)
        published = len([l for l in self.listings.values() if l.status == ListingStatus.PUBLISHED.value])
        total_sales = sum(l.sales for l in self.listings.values())
        total_views = sum(l.views for l in self.listings.values())
        
        return {
            "total_listings": total,
            "published": published,
            "draft": total - published,
            "total_sales": total_sales,
            "total_views": total_views,
            "conversion_rate": (total_sales / total_views * 100) if total_views > 0 else 0
        }
    
    def initialize_default_listings(self):
        """Create default marketplace listings for all products"""
        products = self.product_manager.get_active_products()
        
        for product in products:
            # Create Gumroad listing
            self.create_listing(product.id, MarketplaceType.GUMROAD.value, {
                "price": product.price_usd,
                "currency": "USD"
            })
            
            # Create Shopify listing
            self.create_listing(product.id, MarketplaceType.SHOPIFY.value, {
                "price": product.price_usd,
                "currency": "USD"
            })
        
        logger.info(f"Initialized listings for {len(products)} products")


def main():
    """Test marketplace manager"""
    from core.engine import ConfigManager, DatabaseManager
    from pathlib import Path
    from products.product_manager import ProductManager
    
    config = ConfigManager(Path("config/engine.yaml"))
    db = DatabaseManager(Path(config.get("database.path")))
    pm = ProductManager(db)
    
    mm = MarketplaceManager(config, pm)
    mm.initialize_default_listings()
    
    # Show stats
    stats = mm.get_listing_stats()
    print(f"\nListing Stats:")
    print(f"  Total: {stats['total_listings']}")
    print(f"  Published: {stats['published']}")
    print(f"  Sales: {stats['total_sales']}")
    
    db.close()


if __name__ == "__main__":
    main()
