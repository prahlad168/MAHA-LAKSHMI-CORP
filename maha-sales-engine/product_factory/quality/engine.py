#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Product Quality Engine
Automated quality verification for generated products.
"""

import os
import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

logger = logging.getLogger("maha-sales-engine.product-factory.quality")


class QualityCheck:
    """Individual quality check"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.passed = False
        self.score = 0.0
        self.issues = []
    
    def __repr__(self):
        return f"QualityCheck({self.name}, passed={self.passed}, score={self.score})"


class QualityEngine:
    """Automated product quality verification"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.checks = [
            ("missing_files", "Check for missing required files"),
            ("broken_references", "Check for broken internal references"),
            ("metadata_completeness", "Check metadata completeness"),
            ("minimum_content_size", "Check minimum content size"),
            ("naming_standards", "Check file naming standards"),
            ("folder_structure", "Check folder structure compliance"),
            ("file_integrity", "Check file integrity and corruption"),
            ("license_presence", "Check license file exists"),
            ("description_presence", "Check description file exists"),
            ("preview_assets", "Check preview assets exist")
        ]
    
    def run_quality_check(self, product_id: str) -> Dict[str, Any]:
        """Run all quality checks on a product"""
        try:
            product_dir = self.output_dir / product_id
            
            if not product_dir.exists():
                return {"error": f"Product directory not found: {product_dir}"}
            
            results = []
            total_score = 0.0
            issues = []
            
            for check_name, description in self.checks:
                check = self._run_check(check_name, product_dir)
                results.append({
                    "name": check_name,
                    "description": description,
                    "passed": check.passed,
                    "score": check.score,
                    "issues": check.issues
                })
                total_score += check.score
                issues.extend(check.issues)
            
            overall_score = total_score / len(self.checks) if self.checks else 0.0
            passed = overall_score >= 0.8
            
            report = {
                "product_id": product_id,
                "overall_score": overall_score,
                "passed": passed,
                "checks": results,
                "issues": issues,
                "recommendation": "APPROVED" if passed else "NEEDS_REVIEW",
                "created_at": ""
            }
            report["created_at"] = ""
            
            # Save quality report
            report_path = product_dir / "quality_report.json"
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Quality check complete: {product_id} - Score: {overall_score:.1%}")
            return report
            
        except Exception as e:
            logger.error(f"Quality check failed: {e}")
            return {"error": str(e), "passed": False}
    
    def _run_check(self, check_name: str, product_dir: Path) -> QualityCheck:
        """Run individual quality check"""
        check = QualityCheck(check_name, "")
        
        try:
            if check_name == "missing_files":
                self._check_missing_files(product_dir, check)
            elif check_name == "broken_references":
                self._check_broken_references(product_dir, check)
            elif check_name == "metadata_completeness":
                self._check_metadata_completeness(product_dir, check)
            elif check_name == "minimum_content_size":
                self._check_minimum_content_size(product_dir, check)
            elif check_name == "naming_standards":
                self._check_naming_standards(product_dir, check)
            elif check_name == "folder_structure":
                self._check_folder_structure(product_dir, check)
            elif check_name == "file_integrity":
                self._check_file_integrity(product_dir, check)
            elif check_name == "license_presence":
                self._check_license_presence(product_dir, check)
            elif check_name == "description_presence":
                self._check_description_presence(product_dir, check)
            elif check_name == "preview_assets":
                self._check_preview_assets(product_dir, check)
        except Exception as e:
            check.issues.append(f"Check failed: {str(e)}")
        
        return check
    
    def _check_missing_files(self, product_dir: Path, check: QualityCheck):
        """Check for missing required files"""
        required_files = ["metadata.json", "description.md", "license.txt", "version.json", "history.json"]
        missing = []
        
        for file in required_files:
            if not (product_dir / file).exists():
                missing.append(file)
        
        if missing:
            check.passed = False
            check.score = 0.0
            check.issues = [f"Missing required files: {', '.join(missing)}"]
        else:
            check.passed = True
            check.score = 1.0
    
    def _check_broken_references(self, product_dir: Path, check: QualityCheck):
        """Check for broken internal references"""
        broken = []
        
        # Check metadata references
        metadata_path = product_dir / "metadata.json"
        if metadata_path.exists():
            try:
                with open(metadata_path) as f:
                    metadata = json.load(f)
                
                # Check if referenced paths exist
                if metadata.get("file_path") and not (product_dir / metadata["file_path"]).exists():
                    broken.append(metadata["file_path"])
                
                if metadata.get("preview_path") and not (product_dir / metadata["preview_path"]).exists():
                    broken.append(metadata["preview_path"])
            except:
                pass
        
        if broken:
            check.passed = False
            check.score = 0.0
            check.issues = [f"Broken references: {', '.join(broken)}"]
        else:
            check.passed = True
            check.score = 1.0
    
    def _check_metadata_completeness(self, product_dir: Path, check: QualityCheck):
        """Check metadata completeness"""
        metadata_path = product_dir / "metadata.json"
        if not metadata_path.exists():
            check.passed = False
            check.score = 0.0
            check.issues = ["metadata.json missing"]
            return
        
        try:
            with open(metadata_path) as f:
                metadata = json.load(f)
            
            required_fields = ["product_id", "title", "description", "category", "version", "author", "license"]
            missing = [field for field in required_fields if not metadata.get(field)]
            
            if missing:
                check.passed = False
                check.score = 0.5
                check.issues = [f"Missing metadata fields: {', '.join(missing)}"]
            else:
                check.passed = True
                check.score = 1.0
        except Exception as e:
            check.passed = False
            check.score = 0.0
            check.issues = [f"Invalid metadata.json: {str(e)}"]
    
    def _check_minimum_content_size(self, product_dir: Path, check: QualityCheck):
        """Check minimum content size"""
        product_content_dir = product_dir / "product"
        if not product_content_dir.exists():
            check.passed = False
            check.score = 0.0
            check.issues = ["Product content directory missing"]
            return
        
        total_size = sum(f.stat().st_size for f in product_content_dir.rglob("*") if f.is_file())
        min_size = 512  # 512 bytes minimum for generated products
        
        if total_size < min_size:
            check.passed = False
            check.score = total_size / min_size
            check.issues = [f"Product too small: {total_size} bytes (minimum: {min_size})"]
        else:
            check.passed = True
            check.score = 1.0
    
    def _check_naming_standards(self, product_dir: Path, check: QualityCheck):
        """Check file naming standards"""
        issues = []
        
        for file_path in product_dir.rglob("*"):
            if file_path.is_file():
                filename = file_path.name
                if " " in filename and not file_path.suffix:
                    issues.append(f"File with spaces: {filename}")
        
        if issues:
            check.passed = False
            check.score = 0.7
            check.issues = issues
        else:
            check.passed = True
            check.score = 1.0
    
    def _check_folder_structure(self, product_dir: Path, check: QualityCheck):
        """Check folder structure compliance"""
        required_dirs = ["product", "preview", "thumbnail"]
        missing = []
        
        for dir_name in required_dirs:
            if not (product_dir / dir_name).is_dir():
                missing.append(dir_name)
        
        if missing:
            check.passed = False
            check.score = 0.0
            check.issues = [f"Missing directories: {', '.join(missing)}"]
        else:
            check.passed = True
            check.score = 1.0
    
    def _check_file_integrity(self, product_dir: Path, check: QualityCheck):
        """Check file integrity"""
        corrupt = []
        
        for file_path in product_dir.rglob("*.json"):
            try:
                with open(file_path, encoding="utf-8") as f:
                    json.load(f)
            except:
                corrupt.append(str(file_path.name))
        
        if corrupt:
            check.passed = False
            check.score = 0.0
            check.issues = [f"Corrupt JSON files: {', '.join(corrupt)}"]
        else:
            check.passed = True
            check.score = 1.0
    
    def _check_license_presence(self, product_dir: Path, check: QualityCheck):
        """Check license file exists"""
        license_path = product_dir / "license.txt"
        check.passed = license_path.exists()
        check.score = 1.0 if check.passed else 0.0
        if not check.passed:
            check.issues = ["license.txt missing"]
    
    def _check_description_presence(self, product_dir: Path, check: QualityCheck):
        """Check description file exists"""
        desc_path = product_dir / "description.md"
        check.passed = desc_path.exists()
        check.score = 1.0 if check.passed else 0.0
        if not check.passed:
            check.issues = ["description.md missing"]
    
    def _check_preview_assets(self, product_dir: Path, check: QualityCheck):
        """Check preview assets exist"""
        preview_dir = product_dir / "preview"
        thumbnail_dir = product_dir / "thumbnail"
        
        has_preview = preview_dir.exists() and any(preview_dir.iterdir())
        has_thumbnail = thumbnail_dir.exists() and any(thumbnail_dir.iterdir())
        
        if has_preview and has_thumbnail:
            check.passed = True
            check.score = 1.0
        elif preview_dir.exists() or thumbnail_dir.exists():
            check.passed = True
            check.score = 0.7
            check.issues = ["Preview assets directory exists but may be empty"]
        else:
            check.passed = False
            check.score = 0.0
            check.issues = ["Missing preview and thumbnail assets"]


def main():
    """Test quality engine"""
    from pathlib import Path
    
    output_dir = Path("product-factory/output")
    engine = QualityEngine(output_dir)
    
    # Test with a product
    test_product_id = "ML-20260727-TEST001"
    report = engine.run_quality_check(test_product_id)
    
    print(f"\nQuality Report for {test_product_id}:")
    print(f"  Overall Score: {report.get('overall_score', 0):.1%}")
    print(f"  Passed: {report.get('passed', False)}")
    print(f"  Issues: {len(report.get('issues', []))}")
    print(f"  Recommendation: {report.get('recommendation', 'UNKNOWN')}")


if __name__ == "__main__":
    main()
