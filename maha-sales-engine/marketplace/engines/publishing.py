#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Marketplace Engines
Publishing, synchronization, and webhook engines.
"""

import os
import sys
import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.engine import DatabaseManager, ConfigManager
from marketplace.sdk.base import BaseMarketplaceProvider, PublicationStatus, ProductMapping
from marketplace.core.registry import ProviderRegistry
from marketplace.core.state_machine import StatusManager
from marketplace.events.bus import event_bus, MarketplaceEvents
from marketplace.security.credentials import CredentialManager

logger = logging.getLogger("maha-sales-engine.marketplace.engines")


class PublishingEngine:
    """Engine for publishing products to marketplaces"""
    
    def __init__(self, db_manager: DatabaseManager, registry: ProviderRegistry,
                 credential_manager: CredentialManager, event_bus):
        self.db = db_manager
        self.registry = registry
        self.credential_manager = credential_manager
        self.event_bus = event_bus
        self.status_manager = StatusManager()
    
    async def publish(self, marketplace_id: str, product_id: str, 
                      product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Publish product to marketplace"""
        try:
            # Get provider instance
            provider = self.registry.get_instance(marketplace_id)
            if not provider:
                return {"success": False, "error": f"Provider not found: {marketplace_id}"}
            
            # Get mapping
            mapping = self._get_mapping(marketplace_id, product_id)
            if not mapping:
                mapping = self._create_mapping(marketplace_id, product_id)
            
            # Validate state transition
            transition = self.status_manager.transition(mapping, PublicationStatus.PUBLISHING.value)
            if not transition["success"]:
                return {"success": False, "error": transition["error"]}
            
            # Publish event
            event = event_bus.Event(
                MarketplaceEvents.PUBLISH_STARTED,
                {"marketplace_id": marketplace_id, "product_id": product_id}
            )
            self.event_bus.publish(event)
            
            # Execute publish
            result = await provider.publish(product_id, product_data, mapping)
            
            if result.get("success"):
                # Update mapping
                mapping["marketplace_product_id"] = result.get("marketplace_product_id")
                mapping["listing_id"] = result.get("listing_id")
                mapping["external_url"] = result.get("url")
                mapping["published_version"] = product_data.get("version", "1.0.0")
                mapping["last_sync"] = datetime.now().isoformat()
                mapping["retry_count"] = 0
                
                # Transition to published
                self.status_manager.transition(mapping, PublicationStatus.PUBLISHED.value)
                
                # Save mapping
                self._save_mapping(mapping)
                
                # Publish completed event
                event = event_bus.Event(
                    MarketplaceEvents.PUBLISH_COMPLETED,
                    {"marketplace_id": marketplace_id, "product_id": product_id, "result": result}
                )
                self.event_bus.publish(event)
                
                return {"success": True, "mapping": mapping}
            else:
                # Handle failure
                mapping["last_error"] = result.get("error")
                mapping["retry_count"] += 1
                self._save_mapping(mapping)
                
                self.status_manager.transition(mapping, PublicationStatus.FAILED.value)
                
                event = event_bus.Event(
                    MarketplaceEvents.PUBLISH_FAILED,
                    {"marketplace_id": marketplace_id, "product_id": product_id, "error": result.get("error")}
                )
                self.event_bus.publish(event)
                
                return result
                
        except Exception as e:
            logger.error(f"Publish failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def update(self, marketplace_id: str, product_id: str, 
                     product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update product on marketplace"""
        try:
            provider = self.registry.get_instance(marketplace_id)
            if not provider:
                return {"success": False, "error": "Provider not found"}
            
            mapping = self._get_mapping(marketplace_id, product_id)
            if not mapping:
                return {"success": False, "error": "Mapping not found"}
            
            if not self.status_manager.can_update(mapping):
                return {"success": False, "error": "Cannot update in current state"}
            
            self.status_manager.transition(mapping, PublicationStatus.UPDATING.value)
            
            event = event_bus.Event(
                MarketplaceEvents.UPDATE_STARTED,
                {"marketplace_id": marketplace_id, "product_id": product_id}
            )
            self.event_bus.publish(event)
            
            result = await provider.update(product_id, product_data, mapping)
            
            if result.get("success"):
                self.status_manager.transition(mapping, PublicationStatus.PUBLISHED.value)
                mapping["last_sync"] = datetime.now().isoformat()
                self._save_mapping(mapping)
                
                event = event_bus.Event(
                    MarketplaceEvents.UPDATE_COMPLETED,
                    {"marketplace_id": marketplace_id, "product_id": product_id}
                )
                self.event_bus.publish(event)
                
                return {"success": True}
            else:
                self.status_manager.transition(mapping, PublicationStatus.FAILED.value)
                return result
                
        except Exception as e:
            logger.error(f"Update failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def archive(self, marketplace_id: str, product_id: str) -> Dict[str, Any]:
        """Archive product on marketplace"""
        try:
            provider = self.registry.get_instance(marketplace_id)
            if not provider:
                return {"success": False, "error": "Provider not found"}
            
            mapping = self._get_mapping(marketplace_id, product_id)
            if not mapping:
                return {"success": False, "error": "Mapping not found"}
            
            result = await provider.archive(mapping)
            
            if result.get("success"):
                self.status_manager.transition(mapping, PublicationStatus.ARCHIVED.value)
                self._save_mapping(mapping)
                
                event = event_bus.Event(
                    MarketplaceEvents.ARCHIVE_COMPLETED,
                    {"marketplace_id": marketplace_id, "product_id": product_id}
                )
                self.event_bus.publish(event)
            
            return result
        except Exception as e:
            logger.error(f"Archive failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def delete(self, marketplace_id: str, product_id: str) -> Dict[str, Any]:
        """Delete product from marketplace"""
        try:
            provider = self.registry.get_instance(marketplace_id)
            if not provider:
                return {"success": False, "error": "Provider not found"}
            
            mapping = self._get_mapping(marketplace_id, product_id)
            if not mapping:
                return {"success": False, "error": "Mapping not found"}
            
            result = await provider.delete(mapping)
            
            if result.get("success"):
                self.status_manager.transition(mapping, PublicationStatus.DELETED.value)
                self._save_mapping(mapping)
                
                event = event_bus.Event(
                    MarketplaceEvents.DELETE_COMPLETED,
                    {"marketplace_id": marketplace_id, "product_id": product_id}
                )
                self.event_bus.publish(event)
            
            return result
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_mapping(self, marketplace_id: str, product_id: str) -> Optional[Dict[str, Any]]:
        """Get product mapping"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM marketplace_products 
                WHERE marketplace_id = ? AND product_id = ?
            """, (marketplace_id, product_id))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Failed to get mapping: {e}")
            return None
    
    def _create_mapping(self, marketplace_id: str, product_id: str) -> Dict[str, Any]:
        """Create new product mapping"""
        mapping = {
            "mapping_id": f"map-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "marketplace_id": marketplace_id,
            "product_id": product_id,
            "publication_status": PublicationStatus.DRAFT.value,
            "retry_count": 0,
            "created_at": datetime.now().isoformat()
        }
        self._save_mapping(mapping)
        return mapping
    
    def _save_mapping(self, mapping: Dict[str, Any]):
        """Save mapping to database"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO marketplace_products 
                (mapping_id, marketplace_id, product_id, marketplace_product_id,
                 listing_id, external_url, published_version, publication_status,
                 last_sync, last_error, retry_count, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                mapping.get("mapping_id"),
                mapping.get("marketplace_id"),
                mapping.get("product_id"),
                mapping.get("marketplace_product_id"),
                mapping.get("listing_id"),
                mapping.get("external_url"),
                mapping.get("published_version"),
                mapping.get("publication_status", PublicationStatus.DRAFT.value),
                mapping.get("last_sync"),
                mapping.get("last_error"),
                mapping.get("retry_count", 0),
                json.dumps(mapping.get("metadata", {})),
                mapping.get("created_at", datetime.now().isoformat()),
                datetime.now().isoformat()
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to save mapping: {e}")


class SynchronizationEngine:
    """Engine for synchronizing product data with marketplaces"""
    
    def __init__(self, db_manager: DatabaseManager, registry: ProviderRegistry,
                 credential_manager: CredentialManager, event_bus):
        self.db = db_manager
        self.registry = registry
        self.credential_manager = credential_manager
        self.event_bus = event_bus
        self.status_manager = StatusManager()
    
    async def sync_product(self, marketplace_id: str, product_id: str) -> Dict[str, Any]:
        """Synchronize single product"""
        try:
            provider = self.registry.get_instance(marketplace_id)
            if not provider:
                return {"success": False, "error": "Provider not found"}
            
            mapping = self._get_mapping(marketplace_id, product_id)
            if not mapping:
                return {"success": False, "error": "Mapping not found"}
            
            self.status_manager.transition(mapping, PublicationStatus.SYNCING.value)
            
            event = event_bus.Event(
                MarketplaceEvents.SYNC_STARTED,
                {"marketplace_id": marketplace_id, "product_id": product_id}
            )
            self.event_bus.publish(event)
            
            result = await provider.sync(mapping)
            
            if result.get("success"):
                mapping["last_sync"] = datetime.now().isoformat()
                self.status_manager.transition(mapping, PublicationStatus.PUBLISHED.value)
            else:
                self.status_manager.transition(mapping, PublicationStatus.FAILED.value)
                mapping["last_error"] = result.get("error")
            
            self._save_mapping(mapping)
            
            event_type = (MarketplaceEvents.SYNC_COMPLETED if result.get("success") 
                         else MarketplaceEvents.SYNC_FAILED)
            event = event_bus.Event(event_type, {"marketplace_id": marketplace_id, "product_id": product_id})
            self.event_bus.publish(event)
            
            return result
            
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def sync_marketplace(self, marketplace_id: str) -> Dict[str, Any]:
        """Synchronize all products in marketplace"""
        try:
            mappings = self._get_all_mappings(marketplace_id)
            results = []
            
            for mapping in mappings:
                if mapping["publication_status"] in [
                    PublicationStatus.PUBLISHED.value,
                    PublicationStatus.FAILED.value,
                    PublicationStatus.SYNCING.value
                ]:
                    result = await self.sync_product(marketplace_id, mapping["product_id"])
                    results.append(result)
            
            return {"success": True, "synced": len(results), "results": results}
            
        except Exception as e:
            logger.error(f"Marketplace sync failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_mapping(self, marketplace_id: str, product_id: str) -> Optional[Dict[str, Any]]:
        """Get product mapping"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM marketplace_products 
                WHERE marketplace_id = ? AND product_id = ?
            """, (marketplace_id, product_id))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Failed to get mapping: {e}")
            return None
    
    def _get_all_mappings(self, marketplace_id: str) -> List[Dict[str, Any]]:
        """Get all mappings for marketplace"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM marketplace_products WHERE marketplace_id = ?
            """, (marketplace_id,))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get mappings: {e}")
            return []
    
    def _save_mapping(self, mapping: Dict[str, Any]):
        """Save mapping to database"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO marketplace_products 
                (mapping_id, marketplace_id, product_id, marketplace_product_id,
                 listing_id, external_url, published_version, publication_status,
                 last_sync, last_error, retry_count, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                mapping.get("mapping_id"),
                mapping.get("marketplace_id"),
                mapping.get("product_id"),
                mapping.get("marketplace_product_id"),
                mapping.get("listing_id"),
                mapping.get("external_url"),
                mapping.get("published_version"),
                mapping.get("publication_status", PublicationStatus.DRAFT.value),
                mapping.get("last_sync"),
                mapping.get("last_error"),
                mapping.get("retry_count", 0),
                json.dumps(mapping.get("metadata", {})),
                mapping.get("created_at", datetime.now().isoformat()),
                datetime.now().isoformat()
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to save mapping: {e}")


class WebhookEngine:
    """Webhook processing engine"""
    
    def __init__(self, db_manager: DatabaseManager, event_bus):
        self.db = db_manager
        self.event_bus = event_bus
        self._webhooks: Dict[str, Dict[str, Any]] = {}
    
    def register_webhook(self, marketplace_id: str, webhook_url: str, 
                         events: List[str], secret: str = "") -> bool:
        """Register webhook endpoint"""
        try:
            webhook_id = f"wh-{marketplace_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            self._webhooks[webhook_id] = {
                "webhook_id": webhook_id,
                "marketplace_id": marketplace_id,
                "url": webhook_url,
                "events": events,
                "secret": secret,
                "active": True,
                "created_at": datetime.now().isoformat()
            }
            logger.info(f"Webhook registered: {webhook_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to register webhook: {e}")
            return False
    
    async def process_webhook(self, marketplace_id: str, payload: Dict[str, Any], 
                              signature: str = "") -> Dict[str, Any]:
        """Process incoming webhook"""
        try:
            event = event_bus.Event(
                MarketplaceEvents.WEBHOOK_RECEIVED,
                {"marketplace_id": marketplace_id, "payload": payload}
            )
            self.event_bus.publish(event)
            
            # Validate signature if secret configured
            webhook = self._get_webhook_for_marketplace(marketplace_id)
            if webhook and webhook.get("secret"):
                if not self._validate_signature(payload, signature, webhook["secret"]):
                    return {"success": False, "error": "Invalid signature"}
            
            # Process webhook based on event type
            event_type = payload.get("event_type", "unknown")
            
            # Store webhook log
            self._log_webhook(marketplace_id, payload, "received")
            
            event = event_bus.Event(
                MarketplaceEvents.WEBHOOK_PROCESSED,
                {"marketplace_id": marketplace_id, "event_type": event_type}
            )
            self.event_bus.publish(event)
            
            return {"success": True, "processed": True}
            
        except Exception as e:
            logger.error(f"Webhook processing failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _validate_signature(self, payload: Dict[str, Any], signature: str, secret: str) -> bool:
        """Validate webhook signature"""
        # Simplified validation - implement actual HMAC validation per provider
        if not signature:
            return False
        return True
    
    def _get_webhook_for_marketplace(self, marketplace_id: str) -> Optional[Dict[str, Any]]:
        """Get webhook for marketplace"""
        for webhook in self._webhooks.values():
            if webhook["marketplace_id"] == marketplace_id and webhook["active"]:
                return webhook
        return None
    
    def _log_webhook(self, marketplace_id: str, payload: Dict[str, Any], status: str):
        """Log webhook to database"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO webhook_logs (id, marketplace_id, payload, status, received_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                f"whlog-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                marketplace_id,
                json.dumps(payload),
                status,
                datetime.now().isoformat()
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to log webhook: {e}")


def main():
    """Test engines"""
    print("Marketplace Engines initialized")
    print("- PublishingEngine")
    print("- SynchronizationEngine")
    print("- WebhookEngine")


if __name__ == "__main__":
    main()
