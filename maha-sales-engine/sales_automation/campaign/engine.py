#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Campaign Engine
Campaign management for product launches and promotions.
"""

import os
import sys
import json
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.sales-automation.campaign")


class CampaignType(Enum):
    LAUNCH = "launch"
    UPDATE = "update"
    SEASONAL = "seasonal"
    FLASH_SALE = "flash_sale"
    HOLIDAY = "holiday"
    BUNDLE = "bundle"
    CROSS_MARKETPLACE = "cross_marketplace"
    RECURRING = "recurring"


class CampaignStatus(Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Campaign:
    campaign_id: str
    name: str
    description: str
    campaign_type: str
    status: str
    product_ids: List[str]
    marketplace_ids: List[str]
    schedule: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: str
    updated_at: str


class CampaignEngine:
    """Manage campaign lifecycle"""
    
    def __init__(self, db_manager, workflow_engine, publication_engine, event_bus):
        self.db = db_manager
        self.workflow_engine = workflow_engine
        self.publication_engine = publication_engine
        self.event_bus = event_bus
    
    def create_campaign(self, name: str, campaign_type: str, product_ids: List[str],
                        marketplace_ids: List[str], schedule: Dict[str, Any] = None) -> Optional[str]:
        try:
            campaign_id = f"campaign-{uuid.uuid4().hex[:12]}"
            now = datetime.now().isoformat()
            
            campaign = Campaign(
                campaign_id=campaign_id,
                name=name,
                description=f"{campaign_type} campaign",
                campaign_type=campaign_type,
                status=CampaignStatus.DRAFT.value,
                product_ids=product_ids,
                marketplace_ids=marketplace_ids,
                schedule=schedule or {},
                metadata={},
                created_at=now,
                updated_at=now
            )
            
            self._save_campaign(campaign)
            logger.info(f"Campaign created: {campaign_id}")
            return campaign_id
        except Exception as e:
            logger.error(f"Failed to create campaign: {e}")
            return None
    
    def start_campaign(self, campaign_id: str) -> bool:
        try:
            campaign = self._load_campaign(campaign_id)
            if not campaign:
                return False
            
            campaign.status = CampaignStatus.RUNNING.value
            campaign.updated_at = datetime.now().isoformat()
            self._save_campaign(campaign)
            
            for marketplace_id in campaign.marketplace_ids:
                for product_id in campaign.product_ids:
                    self.publication_engine.publish_single(
                        marketplace_id, product_id, {}
                    )
            
            logger.info(f"Campaign started: {campaign_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to start campaign: {e}")
            return False
    
    def _save_campaign(self, campaign: Campaign):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO campaigns 
                (campaign_id, name, description, campaign_type, status, product_ids,
                 marketplace_ids, schedule, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                campaign.campaign_id, campaign.name, campaign.description,
                campaign.campaign_type, campaign.status,
                json.dumps(campaign.product_ids), json.dumps(campaign.marketplace_ids),
                json.dumps(campaign.schedule), json.dumps(campaign.metadata),
                campaign.created_at, campaign.updated_at
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to save campaign: {e}")
    
    def _load_campaign(self, campaign_id: str) -> Optional[Campaign]:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM campaigns WHERE campaign_id = ?", (campaign_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return Campaign(
                campaign_id=row["campaign_id"],
                name=row["name"],
                description=row["description"],
                campaign_type=row["campaign_type"],
                status=row["status"],
                product_ids=json.loads(row["product_ids"]),
                marketplace_ids=json.loads(row["marketplace_ids"]),
                schedule=json.loads(row["schedule"]),
                metadata=json.loads(row["metadata"]),
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )
        except Exception as e:
            logger.error(f"Failed to load campaign: {e}")
            return None


def main():
    print("Campaign Engine initialized")


if __name__ == "__main__":
    main()
