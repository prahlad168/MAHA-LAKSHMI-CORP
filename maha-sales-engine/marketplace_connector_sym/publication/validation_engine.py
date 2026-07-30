#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Validation Engine
Validates product packages before publication.
"""

import os
import sys
import json
import zipfile
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.marketplace_connector.validation")


@dataclass
class ValidationResult:
    valid: bool
    errors: List[str]
    warnings: List[str]
    score: float
    checked_at: str = field(default_factory=lambda: datetime.now().isoformat())


class ValidationEngine:
    """
    Validation engine for product packages.
    Automatically verify package integrity and reject invalid packages.
    """
    
    def __init__(self):
        self.required_files = [
            "metadata.json",
            "description.md",
            "pricing.json",
            "keywords.json",
            "license.txt",
            "version.json",
            "quality_report.json",
            "history.json"
        ]
        self.required_dirs = ["thumbnail", "product"]
    
    def validate(self, package_path: str, metadata: Dict[str, Any]) -> ValidationResult:
        """Validate complete product package"""
        errors = []
        warnings = []
        
        # Validate structure
        structure_errors = self._validate_structure(package_path)
        errors.extend(structure_errors)
        
        # Validate files
        file_errors = self._validate_files(package_path)
        errors.extend(file_errors)
        
        # Validate metadata
        metadata_errors = self._validate_metadata(metadata)
        errors.extend(metadata_errors)
        
        # Validate ZIP integrity
        zip_errors = self._validate_zip_integrity(package_path)
        errors.extend(zip_errors)
        
        # Calculate score
        total_checks = len(self.required_files) + len(self.required_dirs) + 3
        passed_checks = total_checks - len(errors)
        score = passed_checks / total_checks if total_checks > 0 else 0.0
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            score=score
        )
    
    def _validate_structure(self, package_path: str) -> List[str]:
        """Validate package structure"""
        errors = []
        path = Path(package_path)
        
        # Check required files
        for required_file in self.required_files:
            if not (path / required_file).exists():
                errors.append(f"Missing required file: {required_file}")
        
        # Check required directories
        for required_dir in self.required_dirs:
            if not (path / required_dir).is_dir():
                errors.append(f"Missing required directory: {required_dir}")
        
        return errors
    
    def _validate_files(self, package_path: str) -> List[str]:
        """Validate file contents"""
        errors = []
        path = Path(package_path)
        
        # Validate metadata.json
        metadata_file = path / "metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file) as f:
                    metadata = json.load(f)
                required_metadata = ["title", "description", "price", "currency"]
                for field in required_metadata:
                    if field not in metadata:
                        errors.append(f"Missing metadata field: {field}")
            except json.JSONDecodeError:
                errors.append("Invalid metadata.json format")
        
        # Validate pricing.json
        pricing_file = path / "pricing.json"
        if pricing_file.exists():
            try:
                with open(pricing_file) as f:
                    pricing = json.load(f)
                if "price" not in pricing:
                    errors.append("Missing price in pricing.json")
                elif pricing["price"] < 0:
                    errors.append("Invalid price in pricing.json")
            except json.JSONDecodeError:
                errors.append("Invalid pricing.json format")
        
        # Validate thumbnail
        thumbnail_dir = path / "thumbnail"
        if thumbnail_dir.exists():
            thumbnails = list(thumbnail_dir.glob("*"))
            if not thumbnails:
                errors.append("No thumbnail files found")
        
        # Validate product file
        product_dir = path / "product"
        if product_dir.exists():
            product_files = list(product_dir.glob("*"))
            if not product_files:
                errors.append("No product files found")
        
        return errors
    
    def _validate_metadata(self, metadata: Dict[str, Any]) -> List[str]:
        """Validate metadata"""
        errors = []
        
        required_fields = ["title", "description", "price", "currency", "tags"]
        for field in required_fields:
            if field not in metadata:
                errors.append(f"Missing metadata field: {field}")
        
        # Validate title length
        title = metadata.get("title", "")
        if len(title) < 3:
            errors.append("Title too short (minimum 3 characters)")
        elif len(title) > 200:
            errors.append("Title too long (maximum 200 characters)")
        
        # Validate description
        description = metadata.get("description", "")
        if len(description) < 10:
            errors.append("Description too short (minimum 10 characters)")
        
        # Validate price
        price = metadata.get("price", 0)
        if not isinstance(price, (int, float)) or price < 0:
            errors.append("Invalid price")
        
        # Validate currency
        currency = metadata.get("currency", "")
        valid_currencies = ["USD", "EUR", "GBP", "IDR", "SGD", "MYR"]
        if currency not in valid_currencies:
            errors.append(f"Invalid currency: {currency}")
        
        return errors
    
    def _validate_zip_integrity(self, package_path: str) -> List[str]:
        """Validate ZIP file integrity"""
        errors = []
        path = Path(package_path)
        
        # Find ZIP files
        zip_files = list(path.glob("**/*.zip"))
        for zip_file in zip_files:
            try:
                with zipfile.ZipFile(zip_file, 'r') as zf:
                    # Test ZIP integrity
                    bad_file = zf.testzip()
                    if bad_file:
                        errors.append(f"Corrupted ZIP file: {zip_file.name} (bad file: {bad_file})")
            except zipfile.BadZipFile:
                errors.append(f"Invalid ZIP file: {zip_file.name}")
        
        return errors


def main():
    print("Validation Engine loaded")


if __name__ == "__main__":
    main()
