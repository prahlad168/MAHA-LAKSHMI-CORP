#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - License Management
Manage product licenses.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger("maha-sales-engine.product-factory.licenses")


class LicenseManager:
    """Manage product licenses"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.license_templates = {
            "personal": {
                "name": "Personal Use License",
                "terms": "This product is licensed for personal use only. You may not resell, redistribute, or use this product for commercial purposes.",
                "restrictions": [
                    "No commercial use",
                    "No resale or redistribution",
                    "No modification for resale",
                    "No transfer to third parties"
                ]
            },
            "commercial": {
                "name": "Commercial Use License",
                "terms": "This product is licensed for commercial use. You may use this product in client work, commercial projects, and for revenue-generating activities.",
                "restrictions": [
                    "No resale of original product",
                    "No redistribution of source files",
                    "Must be used in end products only"
                ]
            },
            "extended": {
                "name": "Extended License",
                "terms": "This product includes extended rights. You may resell, redistribute, and use this product in unlimited commercial projects.",
                "restrictions": [
                    "No claiming ownership",
                    "No trademark registration"
                ]
            },
            "custom": {
                "name": "Custom License",
                "terms": "Custom license terms apply. Please refer to the specific license agreement provided with this product.",
                "restrictions": []
            }
        }
    
    def get_license(self, license_type: str) -> Dict[str, Any]:
        """Get license template"""
        return self.license_templates.get(license_type, self.license_templates["personal"])
    
    def create_license(self, product_id: str, license_type: str, custom_terms: str = "") -> bool:
        """Create license for product"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            license_data = self.get_license(license_type)
            
            cursor.execute("""
                INSERT INTO pf_licenses (id, product_id, license_type, terms, restrictions, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                f"LIC-{product_id}",
                product_id,
                license_type,
                custom_terms or license_data["terms"],
                json.dumps(license_data["restrictions"]),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            logger.info(f"License created: {product_id} - {license_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create license: {e}")
            return False
    
    def get_product_license(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get license for product"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pf_licenses WHERE product_id = ?", (product_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get license: {e}")
            return None


def main():
    """Test license manager"""
    from core.engine import ConfigManager, DatabaseManager
    from pathlib import Path
    
    config = ConfigManager(Path("config/engine.yaml"))
    db = DatabaseManager(Path(config.get("database.path")))
    
    manager = LicenseManager(db)
    
    # Test creating license
    test_product_id = "ML-20260727-TEST001"
    success = manager.create_license(test_product_id, "commercial")
    print(f"License created: {success}")
    
    db.close()


if __name__ == "__main__":
    main()
