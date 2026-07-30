#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Marketplace Connector Database Manager
Database operations for marketplace connector.
"""

import os
import sys
import json
import time
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.marketplace_connector.db")


class MarketplaceDatabaseManager:
    """Database manager for marketplace connector"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Ensure marketplace tables exist"""
        schema_path = Path(__file__).parent / "schema.sql"
        if schema_path.exists():
            schema = schema_path.read_text()
            self.db.execute(schema)
            logger.info("Marketplace tables created/verified")
    
    def save_account(self, account: Dict[str, Any]) -> bool:
        """Save marketplace account"""
        try:
            query = """
                INSERT OR REPLACE INTO marketplace_accounts 
                (account_id, provider, name, credentials, active, default, created_at, updated_at, last_sync, token_expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                account.get("account_id"),
                account.get("provider"),
                account.get("name"),
                json.dumps(account.get("credentials", {})),
                account.get("active", 1),
                account.get("default", 0),
                account.get("created_at"),
                account.get("updated_at"),
                account.get("last_sync"),
                account.get("token_expires_at")
            )
            self.db.execute(query, params)
            return True
        except Exception as e:
            logger.error(f"Failed to save account: {e}")
            return False
    
    def save_publication(self, publication: Dict[str, Any]) -> bool:
        """Save publication record"""
        try:
            query = """
                INSERT OR REPLACE INTO marketplace_publications 
                (publication_id, product_id, account_id, provider, status, current_stage, stages_completed, errors, data, created_at, updated_at, published_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                publication.get("publication_id"),
                publication.get("product_id"),
                publication.get("account_id"),
                publication.get("provider"),
                publication.get("status"),
                publication.get("current_stage"),
                json.dumps(publication.get("stages_completed", [])),
                json.dumps(publication.get("errors", [])),
                json.dumps(publication.get("data", {})),
                publication.get("created_at"),
                publication.get("updated_at"),
                publication.get("published_at")
            )
            self.db.execute(query, params)
            return True
        except Exception as e:
            logger.error(f"Failed to save publication: {e}")
            return False
    
    def save_marketplace_product(self, product: Dict[str, Any]) -> bool:
        """Save marketplace product mapping"""
        try:
            query = """
                INSERT OR REPLACE INTO marketplace_products 
                (product_id, internal_product_id, marketplace_product_id, marketplace_url, status, provider, price, currency, visibility, published_at, updated_at, checksum, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                product.get("product_id"),
                product.get("internal_product_id"),
                product.get("marketplace_product_id"),
                product.get("marketplace_url"),
                product.get("status"),
                product.get("provider"),
                product.get("price"),
                product.get("currency"),
                product.get("visibility"),
                product.get("published_at"),
                product.get("updated_at"),
                product.get("checksum"),
                json.dumps(product.get("metadata", {}))
            )
            self.db.execute(query, params)
            return True
        except Exception as e:
            logger.error(f"Failed to save marketplace product: {e}")
            return False


def main():
    print("Marketplace Database Manager loaded")


if __name__ == "__main__":
    main()
