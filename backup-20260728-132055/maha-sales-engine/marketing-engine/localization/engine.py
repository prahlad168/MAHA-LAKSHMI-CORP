#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Localization
Multi-language content support.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.marketing.localization")


class SupportedLanguage(Enum):
    ENGLISH = "en"
    INDONESIAN = "id"
    CHINESE = "zh"
    SPANISH = "es"
    ARABIC = "ar"
    HINDI = "hi"
    THAI = "th"
    VIETNAMESE = "vi"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"


@dataclass
class LocalizedContent:
    """Localized content structure"""
    content_id: str
    product_id: str
    content_type: str
    language: str
    region: str
    currency: str
    culture: str
    content: str
    translation_version: str
    is_machine_translated: bool
    reviewed: bool
    created_at: str


class LocalizationEngine:
    """Manage multi-language content"""
    
    def __init__(self, db_manager, ai_manager):
        self.db = db_manager
        self.ai_manager = ai_manager
        self._supported_languages = [lang.value for lang in SupportedLanguage]
    
    def get_supported_languages(self) -> List[str]:
        """Get supported languages"""
        return self._supported_languages
    
    def localize_content(self, content_id: str, target_language: str, 
                        content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Localize content to target language"""
        try:
            if target_language not in self._supported_languages:
                return {"error": f"Unsupported language: {target_language}"}
            
            # Use AI for translation
            prompt = f"""Translate the following marketing content to {target_language}.
Maintain the marketing tone and style.
Context: {json.dumps(context)}

Content to translate:
{content}

Translation:"""
            
            # Placeholder for AI call
            translated = f"[{target_language}] {content}"
            
            localized = LocalizedContent(
                content_id=content_id,
                product_id=context.get("product_id", ""),
                content_type=context.get("content_type", ""),
                language=target_language,
                region=context.get("region", "global"),
                currency=context.get("currency", "USD"),
                culture=context.get("culture", "western"),
                content=translated,
                translation_version="1.0.0",
                is_machine_translated=True,
                reviewed=False,
                created_at=datetime.now().isoformat()
            )
            
            self._save_localized_content(localized)
            
            return {
                "success": True,
                "content_id": content_id,
                "language": target_language,
                "content": translated
            }
        except Exception as e:
            logger.error(f"Localization failed: {e}")
            return {"error": str(e)}
    
    def _save_localized_content(self, localized: LocalizedContent):
        """Save localized content to database"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO localized_content 
                (content_id, product_id, content_type, language, region, currency, culture,
                 content, translation_version, is_machine_translated, reviewed, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                localized.content_id,
                localized.product_id,
                localized.content_type,
                localized.language,
                localized.region,
                localized.currency,
                localized.culture,
                localized.content,
                localized.translation_version,
                localized.is_machine_translated,
                localized.reviewed,
                localized.created_at
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to save localized content: {e}")
    
    def get_localized_content(self, content_id: str, language: str) -> Optional[Dict[str, Any]]:
        """Get localized content"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM localized_content 
                WHERE content_id = ? AND language = ?
            """, (content_id, language))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
        except Exception as e:
            logger.error(f"Failed to get localized content: {e}")
            return None


def main():
    """Test localization"""
    engine = LocalizationEngine(None, None)
    print(f"Supported languages: {engine.get_supported_languages()}")


if __name__ == "__main__":
    main()
