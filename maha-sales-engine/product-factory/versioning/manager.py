#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Product Versioning System
Version control with rollback support for products.
"""

import os
import json
import hashlib
import logging
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

logger = logging.getLogger("maha-sales-engine.product-factory.versioning")


class VersionManager:
    """Manage product versions and rollback"""
    
    def __init__(self, output_dir: Path, db_manager):
        self.output_dir = output_dir
        self.db = db_manager
    
    def create_version(self, product_id: str, product_dir: Path, changelog: str = "") -> Optional[str]:
        """Create a new version of a product"""
        try:
            version_id = f"VER-{product_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            version_number = self._calculate_next_version(product_id)
            
            # Create version directory
            versions_dir = self.output_dir / product_id / "versions"
            versions_dir.mkdir(exist_ok=True)
            
            version_dir = versions_dir / version_id
            version_dir.mkdir(exist_ok=True)
            
            # Copy product files to version directory
            for file_path in product_dir.rglob("*"):
                if file_path.is_file() and "versions" not in str(file_path):
                    relative_path = file_path.relative_to(product_dir)
                    dest_path = version_dir / relative_path
                    dest_path.parent.mkdir(exist_ok=True, parents=True)
                    shutil.copy2(file_path, dest_path)
            
            # Calculate file hash and size
            file_hash = self._calculate_directory_hash(version_dir)
            total_size = sum(f.stat().st_size for f in version_dir.rglob("*") if f.is_file())
            
            # Save version metadata
            version_metadata = {
                "version_id": version_id,
                "product_id": product_id,
                "version_number": version_number,
                "created_at": datetime.now().isoformat(),
                "created_by": "system",
                "changelog": changelog or f"Version {version_number} release",
                "file_path": str(version_dir),
                "file_hash": file_hash,
                "file_size": total_size
            }
            
            with open(version_dir / "version_metadata.json", "w", encoding="utf-8") as f:
                json.dump(version_metadata, f, indent=2)
            
            # Save to database
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO pf_product_versions (
                    id, product_id, version_number, created_at, created_by,
                    changelog, file_path, file_hash, file_size, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                version_id,
                product_id,
                version_number,
                datetime.now().isoformat(),
                "system",
                changelog,
                str(version_dir),
                file_hash,
                total_size,
                json.dumps(version_metadata)
            ))
            
            # Update product version count
            cursor.execute("""
                UPDATE pf_products SET version_count = version_count + 1, updated_at = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), product_id))
            
            conn.commit()
            
            logger.info(f"Version created: {version_id} for product {product_id}")
            return version_id
            
        except Exception as e:
            logger.error(f"Failed to create version: {e}")
            return None
    
    def rollback_version(self, product_id: str, version_id: str) -> bool:
        """Rollback product to a specific version"""
        try:
            # Get version directory
            version_dir = self.output_dir / product_id / "versions" / version_id
            
            if not version_dir.exists():
                logger.error(f"Version not found: {version_id}")
                return False
            
            # Get current product directory
            product_dir = self.output_dir / product_id
            
            # Backup current version
            backup_dir = self.output_dir / product_id / "backup" / datetime.now().strftime("%Y%m%d%H%M%S")
            backup_dir.mkdir(exist_ok=True, parents=True)
            
            for file_path in product_dir.rglob("*"):
                if file_path.is_file() and "versions" not in str(file_path) and "backup" not in str(file_path):
                    relative_path = file_path.relative_to(product_dir)
                    dest_path = backup_dir / relative_path
                    dest_path.parent.mkdir(exist_ok=True, parents=True)
                    shutil.copy2(file_path, dest_path)
            
            # Restore from version
            for file_path in version_dir.rglob("*"):
                if file_path.is_file():
                    relative_path = file_path.relative_to(version_dir)
                    dest_path = product_dir / relative_path
                    dest_path.parent.mkdir(exist_ok=True, parents=True)
                    shutil.copy2(file_path, dest_path)
            
            logger.info(f"Product rolled back: {product_id} to version {version_id}")
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    def get_version_history(self, product_id: str) -> List[Dict[str, Any]]:
        """Get version history for a product"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, version_number, created_at, created_by, changelog, file_size
                FROM pf_product_versions
                WHERE product_id = ?
                ORDER BY created_at DESC
            """, (product_id,))
            
            versions = []
            for row in cursor.fetchall():
                versions.append({
                    "version_id": row[0],
                    "version_number": row[1],
                    "created_at": row[2],
                    "created_by": row[3],
                    "changelog": row[4],
                    "file_size": row[5]
                })
            
            return versions
            
        except Exception as e:
            logger.error(f"Failed to get version history: {e}")
            return []
    
    def _calculate_next_version(self, product_id: str) -> str:
        """Calculate next version number"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT version_number FROM pf_product_versions
                WHERE product_id = ?
                ORDER BY created_at DESC LIMIT 1
            """, (product_id,))
            
            row = cursor.fetchone()
            if row:
                current_version = row[0]
                parts = current_version.split(".")
                if len(parts) == 3:
                    major, minor, patch = map(int, parts)
                    patch += 1
                    return f"{major}.{minor}.{patch}"
            
            return "1.0.0"
            
        except Exception:
            return "1.0.0"
    
    def _calculate_directory_hash(self, directory: Path) -> str:
        """Calculate hash of all files in directory"""
        hasher = hashlib.sha256()
        
        for file_path in sorted(directory.rglob("*")):
            if file_path.is_file():
                hasher.update(str(file_path.relative_to(directory)).encode())
                hasher.update(str(file_path.stat().st_size).encode())
        
        return hasher.hexdigest()


def main():
    """Test versioning"""
    from core.engine import ConfigManager, DatabaseManager
    from pathlib import Path
    
    config = ConfigManager(Path("config/engine.yaml"))
    db = DatabaseManager(Path(config.get("database.path")))
    
    version_manager = VersionManager(OUTPUT_DIR, db)
    
    # Test version creation
    test_product_id = "ML-20260727-TEST001"
    version_id = version_manager.create_version(
        test_product_id,
        OUTPUT_DIR / test_product_id,
        "Initial version"
    )
    
    if version_id:
        print(f"Version created: {version_id}")
        
        # Get version history
        history = version_manager.get_version_history(test_product_id)
        print(f"Version history: {len(history)} versions")
    
    db.close()


if __name__ == "__main__":
    main()
