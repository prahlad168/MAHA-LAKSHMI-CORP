#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Brand Engine
Centralize brand voice, rules, and consistency.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.marketing.brand")


@dataclass
class BrandRules:
    """Brand rules configuration"""
    brand_name: str
    voice: str
    tone: str
    writing_style: str
    forbidden_terms: List[str]
    preferred_terms: Dict[str, str]
    legal_requirements: List[str]
    target_audience: str
    value_proposition: str
    usp: str
    created_at: str
    updated_at: str


class BrandEngine:
    """Manage brand consistency across all content"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self._cache: Dict[str, BrandRules] = {}
    
    def create_brand_rules(self, brand_name: str, rules: Dict[str, Any]) -> bool:
        """Create or update brand rules"""
        try:
            now = datetime.now().isoformat()
            
            brand = BrandRules(
                brand_name=brand_name,
                voice=rules.get("voice", "professional"),
                tone=rules.get("tone", "confident"),
                writing_style=rules.get("writing_style", "clear"),
                forbidden_terms=rules.get("forbidden_terms", []),
                preferred_terms=rules.get("preferred_terms", {}),
                legal_requirements=rules.get("legal_requirements", []),
                target_audience=rules.get("target_audience", ""),
                value_proposition=rules.get("value_proposition", ""),
                usp=rules.get("usp", ""),
                created_at=now,
                updated_at=now
            )
            
            # Save to database
            self._save_brand(brand)
            self._cache[brand_name] = brand
            
            logger.info(f"Brand rules created: {brand_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create brand rules: {e}")
            return False
    
    def get_brand_rules(self, brand_name: str) -> Optional[BrandRules]:
        """Get brand rules"""
        if brand_name in self._cache:
            return self._cache[brand_name]
        
        brand = self._load_brand(brand_name)
        if brand:
            self._cache[brand_name] = brand
        return brand
    
    def validate_content(self, content: str, brand_name: str) -> Dict[str, Any]:
        """Validate content against brand rules"""
        try:
            brand = self.get_brand_rules(brand_name)
            if not brand:
                return {"valid": True, "warnings": ["No brand rules found"]}
            
            issues = []
            
            # Check forbidden terms
            for term in brand.forbidden_terms:
                if term.lower() in content.lower():
                    issues.append(f"Forbidden term: {term}")
            
            # Check preferred terms
            for term, replacement in brand.preferred_terms.items():
                if term.lower() in content.lower():
                    issues.append(f"Use '{replacement}' instead of '{term}'")
            
            return {
                "valid": len(issues) == 0,
                "issues": issues,
                "brand": brand_name
            }
        except Exception as e:
            logger.error(f"Brand validation failed: {e}")
            return {"valid": False, "error": str(e)}
    
    def _save_brand(self, brand: BrandRules):
        """Save brand rules to database"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO brand_rules 
                (brand_name, voice, tone, writing_style, forbidden_terms, preferred_terms,
                 legal_requirements, target_audience, value_proposition, usp, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                brand.brand_name,
                brand.voice,
                brand.tone,
                brand.writing_style,
                json.dumps(brand.forbidden_terms),
                json.dumps(brand.preferred_terms),
                json.dumps(brand.legal_requirements),
                brand.target_audience,
                brand.value_proposition,
                brand.usp,
                brand.created_at,
                brand.updated_at
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to save brand: {e}")
    
    def _load_brand(self, brand_name: str) -> Optional[BrandRules]:
        """Load brand rules from database"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM brand_rules WHERE brand_name = ?", (brand_name,))
            row = cursor.fetchone()
            
            if row:
                return BrandRules(
                    brand_name=row["brand_name"],
                    voice=row["voice"],
                    tone=row["tone"],
                    writing_style=row["writing_style"],
                    forbidden_terms=json.loads(row.get("forbidden_terms", "[]")),
                    preferred_terms=json.loads(row.get("preferred_terms", "{}")),
                    legal_requirements=json.loads(row.get("legal_requirements", "[]")),
                    target_audience=row["target_audience"],
                    value_proposition=row["value_proposition"],
                    usp=row["usp"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"]
                )
            return None
        except Exception as e:
            logger.error(f"Failed to load brand: {e}")
            return None


def main():
    """Test brand engine"""
    print("Brand Engine initialized")


if __name__ == "__main__":
    main()
