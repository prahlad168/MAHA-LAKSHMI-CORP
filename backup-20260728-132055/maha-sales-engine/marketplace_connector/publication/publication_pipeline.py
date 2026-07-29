#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Publication Pipeline
Orchestrates the product publication workflow.
"""

import os
import sys
import json
import time
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from marketplace_connector.core.marketplace_provider import MarketplaceProvider, ProviderType, PublicationStatus, PublicationResult

logger = logging.getLogger("maha-sales-engine.marketplace_connector.publication")


class PipelineStage(Enum):
    LOAD = "load"
    VALIDATE_STRUCTURE = "validate_structure"
    VALIDATE_FILES = "validate_files"
    VALIDATE_METADATA = "validate_metadata"
    BUILD_PAYLOAD = "build_payload"
    UPLOAD_PRODUCT = "upload_product"
    UPLOAD_THUMBNAIL = "upload_thumbnail"
    UPLOAD_PREVIEW = "upload_preview"
    CREATE_LISTING = "create_listing"
    APPLY_DESCRIPTION = "apply_description"
    APPLY_PRICING = "apply_pricing"
    APPLY_TAGS = "apply_tags"
    PUBLISH = "publish"
    STORE_IDS = "store_ids"
    GENERATE_REPORT = "generate_report"
    NOTIFY = "notify"


@dataclass
class PublicationContext:
    publication_id: str
    product_id: str
    provider: str
    status: PublicationStatus
    current_stage: PipelineStage
    stages_completed: List[PipelineStage]
    errors: List[Dict[str, Any]]
    data: Dict[str, Any]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


class PublicationPipeline:
    """
    Publication pipeline that orchestrates the product publication workflow.
    """
    
    def __init__(self, provider, validation_engine, db_manager):
        self.provider = provider
        self.validation_engine = validation_engine
        self.db_manager = db_manager
        self._stages = list(PipelineStage)
    
    async def execute(self, product_path: str, metadata: Dict[str, Any]) -> PublicationResult:
        """Execute publication pipeline"""
        publication_id = f"pub-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
        context = PublicationContext(
            publication_id=publication_id,
            product_id=metadata.get("product_id", ""),
            provider=metadata.get("provider", "gumroad"),
            status=PublicationStatus.QUEUED,
            current_stage=PipelineStage.LOAD,
            stages_completed=[],
            errors=[],
            data={}
        )
        
        try:
            for stage in self._stages:
                context.current_stage = stage
                result = await self._execute_stage(stage, product_path, metadata, context)
                
                if not result.get("success", False):
                    context.status = PublicationStatus.FAILED
                    context.errors.append({
                        "stage": stage.value,
                        "error": result.get("error", "Unknown error"),
                        "timestamp": datetime.now().isoformat()
                    })
                    return PublicationResult(
                        success=False,
                        marketplace_product_id=None,
                        marketplace_url=None,
                        status=PublicationStatus.FAILED,
                        message=result.get("error", "Pipeline failed"),
                        data={"publication_id": publication_id, "errors": context.errors}
                    )
                
                context.stages_completed.append(stage)
                context.data.update(result.get("data", {}))
            
            context.status = PublicationStatus.PUBLISHED
            return PublicationResult(
                success=True,
                marketplace_product_id=context.data.get("marketplace_product_id"),
                marketplace_url=context.data.get("marketplace_url"),
                status=PublicationStatus.PUBLISHED,
                message="Publication successful",
                data=context.data
            )
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            context.status = PublicationStatus.FAILED
            return PublicationResult(
                success=False,
                marketplace_product_id=None,
                marketplace_url=None,
                status=PublicationStatus.FAILED,
                message=str(e),
                data={"publication_id": publication_id}
            )
    
    async def _execute_stage(self, stage: PipelineStage, product_path: str, metadata: Dict[str, Any], context: PublicationContext) -> Dict[str, Any]:
        """Execute single pipeline stage"""
        logger.info(f"Executing stage: {stage.value}")
        
        if stage == PipelineStage.LOAD:
            return await self._stage_load(product_path, metadata)
        elif stage == PipelineStage.VALIDATE_STRUCTURE:
            return await self._stage_validate_structure(product_path)
        elif stage == PipelineStage.VALIDATE_FILES:
            return await self._stage_validate_files(product_path)
        elif stage == PipelineStage.VALIDATE_METADATA:
            return await self._stage_validate_metadata(product_path, metadata)
        elif stage == PipelineStage.BUILD_PAYLOAD:
            return await self._stage_build_payload(metadata, context)
        elif stage == PipelineStage.UPLOAD_PRODUCT:
            return await self._stage_upload_product(product_path, context)
        elif stage == PipelineStage.UPLOAD_THUMBNAIL:
            return await self._stage_upload_thumbnail(product_path, context)
        elif stage == PipelineStage.UPLOAD_PREVIEW:
            return await self._stage_upload_preview(product_path, context)
        elif stage == PipelineStage.CREATE_LISTING:
            return await self._stage_create_listing(metadata, context)
        elif stage == PipelineStage.APPLY_DESCRIPTION:
            return await self._stage_apply_description(metadata, context)
        elif stage == PipelineStage.APPLY_PRICING:
            return await self._stage_apply_pricing(metadata, context)
        elif stage == PipelineStage.APPLY_TAGS:
            return await self._stage_apply_tags(metadata, context)
        elif stage == PipelineStage.PUBLISH:
            return await self._stage_publish(context)
        elif stage == PipelineStage.STORE_IDS:
            return await self._stage_store_ids(context)
        elif stage == PipelineStage.GENERATE_REPORT:
            return await self._stage_generate_report(context)
        elif stage == PipelineStage.NOTIFY:
            return await self._stage_notify(context)
        
        return {"success": True}
    
    async def _stage_load(self, product_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Load product package"""
        if not os.path.exists(product_path):
            return {"success": False, "error": "Product path not found"}
        return {"success": True, "data": {"product_path": product_path}}
    
    async def _stage_validate_structure(self, product_path: str) -> Dict[str, Any]:
        """Validate package structure"""
        required_files = ["metadata.json", "description.md", "pricing.json", "keywords.json"]
        missing = [f for f in required_files if not Path(product_path, f).exists()]
        if missing:
            return {"success": False, "error": f"Missing files: {missing}"}
        return {"success": True}
    
    async def _stage_validate_files(self, product_path: str) -> Dict[str, Any]:
        """Validate required files"""
        # Check thumbnail
        thumbnail_dir = Path(product_path, "thumbnail")
        if not thumbnail_dir.exists() or not list(thumbnail_dir.glob("*")):
            return {"success": False, "error": "Thumbnail missing"}
        return {"success": True}
    
    async def _stage_validate_metadata(self, product_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate metadata"""
        result = self.validation_engine.validate(product_path, metadata)
        valid = result.get("valid") if isinstance(result, dict) else result.valid
        if not valid:
            errors = result.get("errors") if isinstance(result, dict) else result.errors
            return {"success": False, "error": f"Metadata validation failed: {errors}"}
        return {"success": True}
    
    async def _stage_build_payload(self, metadata: Dict[str, Any], context: PublicationContext) -> Dict[str, Any]:
        """Build provider payload"""
        payload = {
            "title": metadata.get("title", ""),
            "description": metadata.get("description", ""),
            "price": metadata.get("price", 0),
            "currency": metadata.get("currency", "USD"),
            "tags": metadata.get("tags", [])
        }
        return {"success": True, "data": {"payload": payload}}
    
    async def _stage_upload_product(self, product_path: str, context: PublicationContext) -> Dict[str, Any]:
        """Upload product file"""
        product_file = Path(product_path, "product", "main.zip")
        if not product_file.exists():
            return {"success": False, "error": "Product file not found"}
        
        result = await self.provider.upload_file(str(product_file), "product")
        if not result.get("success"):
            return {"success": False, "error": result.get("error")}
        
        context.data["product_file_url"] = result.get("file_url")
        return {"success": True, "data": {"product_file_url": result.get("file_url")}}
    
    async def _stage_upload_thumbnail(self, product_path: str, context: PublicationContext) -> Dict[str, Any]:
        """Upload thumbnail"""
        thumbnail_files = list(Path(product_path, "thumbnail").glob("*"))
        if not thumbnail_files:
            return {"success": False, "error": "No thumbnail found"}
        
        result = await self.provider.upload_thumbnail(str(thumbnail_files[0]))
        if not result.get("success"):
            return {"success": False, "error": result.get("error")}
        
        context.data["thumbnail_url"] = result.get("file_url")
        return {"success": True, "data": {"thumbnail_url": result.get("file_url")}}
    
    async def _stage_upload_preview(self, product_path: str, context: PublicationContext) -> Dict[str, Any]:
        """Upload preview assets"""
        preview_dir = Path(product_path, "preview")
        if not preview_dir.exists():
            return {"success": True}  # Preview is optional
        
        preview_files = list(preview_dir.glob("*"))
        if not preview_files:
            return {"success": True}
        
        # Upload previews
        preview_urls = []
        for preview_file in preview_files:
            result = await self.provider.upload_file(str(preview_file), "preview")
            if result.get("success"):
                preview_urls.append(result.get("file_url"))
        
        context.data["preview_urls"] = preview_urls
        return {"success": True, "data": {"preview_urls": preview_urls}}
    
    async def _stage_create_listing(self, metadata: Dict[str, Any], context: PublicationContext) -> Dict[str, Any]:
        """Create listing"""
        payload = context.data.get("payload", {})
        payload["file_url"] = context.data.get("product_file_url")
        payload["thumbnail_url"] = context.data.get("thumbnail_url")
        
        result = await self.provider.create_listing(payload)
        if not result.get("success"):
            return {"success": False, "error": result.get("error")}
        
        context.data["marketplace_product_id"] = result.get("product_id")
        context.data["marketplace_url"] = result.get("url")
        return {"success": True, "data": {"marketplace_product_id": result.get("product_id")}}
    
    async def _stage_apply_description(self, metadata: Dict[str, Any], context: PublicationContext) -> Dict[str, Any]:
        """Apply description"""
        # Description is applied during listing creation
        return {"success": True}
    
    async def _stage_apply_pricing(self, metadata: Dict[str, Any], context: PublicationContext) -> Dict[str, Any]:
        """Apply pricing"""
        # Pricing is applied during listing creation
        return {"success": True}
    
    async def _stage_apply_tags(self, metadata: Dict[str, Any], context: PublicationContext) -> Dict[str, Any]:
        """Apply tags"""
        # Tags are applied during listing creation
        return {"success": True}
    
    async def _stage_publish(self, context: PublicationContext) -> Dict[str, Any]:
        """Publish listing"""
        marketplace_product_id = context.data.get("marketplace_product_id")
        if not marketplace_product_id:
            return {"success": False, "error": "No product ID"}
        
        result = await self.provider.publish(marketplace_product_id)
        if not result.get("success"):
            return {"success": False, "error": result.get("error")}
        
        return {"success": True}
    
    async def _stage_store_ids(self, context: PublicationContext) -> Dict[str, Any]:
        """Store marketplace IDs"""
        # In production, save to database
        return {"success": True}
    
    async def _stage_generate_report(self, context: PublicationContext) -> Dict[str, Any]:
        """Generate publication report"""
        report = {
            "publication_id": context.publication_id,
            "product_id": context.product_id,
            "provider": context.provider,
            "status": context.status.value,
            "stages_completed": [s.value for s in context.stages_completed],
            "marketplace_product_id": context.data.get("marketplace_product_id"),
            "marketplace_url": context.data.get("marketplace_url"),
            "published_at": datetime.now().isoformat()
        }
        context.data["report"] = report
        return {"success": True, "data": {"report": report}}
    
    async def _stage_notify(self, context: PublicationContext) -> Dict[str, Any]:
        """Notify sales automation"""
        # In production, send notification
        return {"success": True}


def main():
    print("Publication Pipeline loaded")


if __name__ == "__main__":
    main()
