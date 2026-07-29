#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Product Packaging
Package and export products in multiple formats.
"""

import os
import json
import zipfile
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger("maha-sales-engine.product-factory.packaging")


class ProductPackager:
    """Package products for distribution"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.packages_dir = output_dir / "packages"
        self.packages_dir.mkdir(exist_ok=True)
    
    def create_zip_package(self, product_id: str, product_dir: Path, include_versions: bool = False) -> Optional[str]:
        """Create ZIP package of product"""
        try:
            zip_filename = f"{product_id}_v1.0.0.zip"
            zip_path = self.packages_dir / zip_filename
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add main product files
                for file_path in product_dir.rglob("*"):
                    if file_path.is_file():
                        if not include_versions and "versions" in str(file_path):
                            continue
                        arcname = str(file_path.relative_to(product_dir))
                        zipf.write(file_path, arcname)
            
            package_size = zip_path.stat().st_size
            logger.info(f"ZIP package created: {zip_path} ({package_size} bytes)")
            
            return str(zip_path)
            
        except Exception as e:
            logger.error(f"Failed to create ZIP package: {e}")
            return None
    
    def create_folder_export(self, product_id: str, product_dir: Path, include_versions: bool = False) -> Optional[str]:
        """Create folder export of product"""
        try:
            export_dir = self.packages_dir / f"{product_id}_export"
            
            if export_dir.exists():
                shutil.rmtree(export_dir)
            
            shutil.copytree(product_dir, export_dir, ignore=shutil.ignore_patterns("versions") if not include_versions else None)
            
            logger.info(f"Folder export created: {export_dir}")
            return str(export_dir)
            
        except Exception as e:
            logger.error(f"Failed to create folder export: {e}")
            return None
    
    def create_manifest(self, product_id: str, product_dir: Path, package_path: str) -> Dict[str, Any]:
        """Create JSON manifest for package"""
        try:
            manifest = {
                "product_id": product_id,
                "package_path": package_path,
                "created_at": datetime.now().isoformat(),
                "files": [],
                "total_files": 0,
                "total_size_bytes": 0,
                "checksum": ""
            }
            
            total_size = 0
            for file_path in product_dir.rglob("*"):
                if file_path.is_file():
                    file_info = {
                        "path": str(file_path.relative_to(product_dir)),
                        "size": file_path.stat().st_size,
                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    }
                    manifest["files"].append(file_info)
                    total_size += file_info["size"]
            
            manifest["total_files"] = len(manifest["files"])
            manifest["total_size_bytes"] = total_size
            manifest["checksum"] = self._calculate_checksum(manifest["files"])
            
            manifest_path = self.packages_dir / f"{product_id}_manifest.json"
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)
            
            return manifest
            
        except Exception as e:
            logger.error(f"Failed to create manifest: {e}")
            return {}
    
    def _calculate_checksum(self, files: List[Dict]) -> str:
        """Calculate checksum for package"""
        import hashlib
        hasher = hashlib.sha256()
        
        for file_info in sorted(files, key=lambda x: x["path"]):
            hasher.update(file_info["path"].encode())
            hasher.update(str(file_info["size"]).encode())
        
        return hasher.hexdigest()[:16]
    
    def get_package_info(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get package information"""
        try:
            manifest_path = self.packages_dir / f"{product_id}_manifest.json"
            if not manifest_path.exists():
                return None
            
            with open(manifest_path) as f:
                return json.load(f)
            
        except Exception as e:
            logger.error(f"Failed to get package info: {e}")
            return None
    
    def list_packages(self) -> List[Dict[str, Any]]:
        """List all available packages"""
        packages = []
        
        for manifest_path in self.packages_dir.glob("*_manifest.json"):
            try:
                with open(manifest_path) as f:
                    manifest = json.load(f)
                packages.append(manifest)
            except:
                continue
        
        return packages


def main():
    """Test packager"""
    from core.engine import ConfigManager, DatabaseManager
    from pathlib import Path
    
    config = ConfigManager(Path("config/engine.yaml"))
    db = DatabaseManager(Path(config.get("database.path")))
    
    output_dir = Path("product-factory/output")
    packager = ProductPackager(output_dir)
    
    # Test with a product
    test_product_id = "ML-20260727-TEST001"
    product_dir = output_dir / test_product_id
    
    if product_dir.exists():
        # Create ZIP package
        zip_path = packager.create_zip_package(test_product_id, product_dir)
        if zip_path:
            print(f"ZIP created: {zip_path}")
        
        # Create manifest
        manifest = packager.create_manifest(test_product_id, product_dir, zip_path or "")
        print(f"Manifest: {manifest.get('total_files', 0)} files")
    
    db.close()


if __name__ == "__main__":
    main()
