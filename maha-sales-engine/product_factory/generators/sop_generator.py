# SOP_BASE_GENERATOR.py

"""
MAHA SALES ENGINE V1 - Base SOP Generator
Abstract base class for all SOP (Standard Operating Procedure) generators.

This provides a plugin architecture for industry-specific SOP generation
without modifying core architecture.
"""

import json
import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger("maha-sales-engine.sop-generator.base")


class PluginInfo:
    """Information about an SOP plugin"""

    def __init__(
        self,
        name: str,
        version: str,
        industry: str,
        compliance_standards: List[str],
        template_categories: List[str],
        description: str = ""
    ):
        self.name = name
        self.version = version
        self.industry = industry
        self.compliance_standards = compliance_standards
        self.template_categories = template_categories
        self.description = description
        self.plugin_id = f"{industry[:3]}-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"
        self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plugin_id": self.plugin_id,
            "name": self.name,
            "version": self.version,
            "industry": self.industry,
            "compliance_standards": self.compliance_standards,
            "template_categories": self.template_categories,
            "description": self.description,
            "created_at": self.created_at
        }


class SOPGenerator(ABC):
    """Abstract base class for all SOP generators"""

    def __init__(self, output_dir: Path, config: Dict[str, Any] = None):
        self.output_dir = output_dir
        self.config = config or {}
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(f"maha-sales-engine.sop-generator.{self.__class__.__name__}")

    @abstractmethod
    def get_info(self) -> PluginInfo:
        """Return plugin information"""
        pass

    @abstractmethod
    def generate(self, product_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate SOP package for given product ID and parameters.

        Args:
            product_id: Globally unique product ID
            parameters: Generation parameters specific to this plugin

        Returns:
            Dictionary with generation results including:
            - product_id
            - generation_status
            - file_count
            - quality_score
            - template_count
            - generated_files
        """
        pass

    def validate_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize generation parameters.

        Args:
            parameters: Raw input parameters

        Returns:
            Validated and normalized parameters
        """
        return parameters

    def create_structure(self, product_id: str) -> Path:
        """
        Create standard SOP package structure.

        Args:
            product_id: Product ID for the package

        Returns:
            Path to the product directory
        """
        product_dir = self.output_dir / product_id
        product_dir.mkdir(parents=True, exist_ok=True)

        # Create standard folders
        (product_dir / "sop_templates").mkdir(exist_ok=True)
        (product_dir / "implementation_checklist").mkdir(exist_ok=True)
        (product_dir / "ai_prompt_package").mkdir(exist_ok=True)
        (product_dir / "preview").mkdir(exist_ok=True)
        (product_dir / "thumbnail").mkdir(exist_ok=True)

        return product_dir

    def save_metadata(self, product_dir: Path, metadata: Dict[str, Any]):
        """Save metadata.json file"""
        with open(product_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

    def save_description(self, product_dir: Path, title: str, description: str):
        """Save description.md file"""
        with open(product_dir / "description.md", "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n")
            f.write(f"{description}\n\n")
            f.write("## SOP Package Overview\n\n")
            f.write("This {title} package contains professionally generated Standard Operating Procedure templates\n")
            f.write("following {self.get_info().industry} industry standards and compliance requirements.\n\n")

    def save_license(self, product_dir: Path, license_type: str = "commercial"):
        """Save license.txt file"""
        licenses = {
            "personal": "PERSONAL USE LICENSE\n\nThis SOP package is licensed for personal use only. You may not resell, redistribute, or use this product for commercial purposes.",
            "commercial": "COMMERCIAL USE LICENSE\n\nThis SOP package is licensed for commercial use. You may use this package in client work, commercial projects, and for revenue-generating activities.",
            "extended": "EXTENDED LICENSE\n\nThis SOP package includes extended rights. You may resell, redistribute, and use this package in unlimited commercial projects.",
            "custom": "CUSTOM LICENSE\n\nPlease refer to the custom license agreement provided with this package."
        }

        with open(product_dir / "license.txt", "w", encoding="utf-8") as f:
            f.write(licenses.get(license_type, licenses["commercial"]))

    def save_keywords(self, product_dir: Path, keywords: List[str]):
        """Save keywords.json file"""
        keywords_data = {
            "keywords": keywords,
            "primary_keywords": keywords[:5],
            "secondary_keywords": keywords[5:15] if len(keywords) > 5 else [],
            "long_tail_keywords": keywords[15:] if len(keywords) > 15 else []
        }

        with open(product_dir / "keywords.json", "w", encoding="utf-8") as f:
            json.dump(keywords_data, f, indent=2, ensure_ascii=False)

    def save_pricing(self, product_dir: Path, price_usd: float, price_idr: float):
        """Save pricing.json file"""
        pricing = {
            "price_usd": price_usd,
            "price_idr": price_idr,
            "currency": "USD",
            "alternate_currency": "IDR",
            "exchange_rate": 16000,
            "last_updated": datetime.now().isoformat(),
            "market_specific_pricing": {
                "id": {"price_idr": price_idr, "currency": "IDR"},
                "en": {"price_usd": price_usd, "currency": "USD"},
                "pt": {"price_usd": price_usd, "currency": "USD"},
                "zh": {"price_usd": price_usd, "currency": "USD"}
            }
        }

        with open(product_dir / "pricing.json", "w", encoding="utf-8") as f:
            json.dump(pricing, f, indent=2)

    def save_version(self, product_dir: Path, version: str = "1.0.0"):
        """Save version.json file"""
        version_data = {
            "current_version": version,
            "version_history": [
                {
                    "version": version,
                    "created_at": datetime.now().isoformat(),
                    "changes": "Initial release",
                    "author": "MAHA LAKSHMI"
                }
            ]
        }

        with open(product_dir / "version.json", "w", encoding="utf-8") as f:
            json.dump(version_data, f, indent=2)

    def save_history(self, product_dir: Path, title: str):
        """Save history.json file"""
        history = {
            "product_title": title,
            "creation_date": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "versions": [],
            "changes": [
                {
                    "date": datetime.now().isoformat(),
                    "version": "1.0.0",
                    "changes": "Initial SOP package creation",
                    "author": "MAHA LAKSHMI"
                }
            ]
        }

        with open(product_dir / "history.json", "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)

    def create_quality_report(self, product_id: str, overall_score: float, passed: bool, issues: List[str]) -> Dict[str, Any]:
        """Create quality report structure"""
        return {
            "product_id": product_id,
            "overall_score": overall_score,
            "passed": passed,
            "checks": [],
            "issues": issues,
            "recommendation": "APPROVED" if passed else "NEEDS_REVIEW",
            "created_at": datetime.now().isoformat()
        }

    def register_generator(self, generator_name: str):
        """Register this generator with ProductFactory"""
        try:
            # This would typically import ProductFactory and register
            # For now, we'll just log the registration
            self.logger.info(f"SOP Generator '{generator_name}' registered successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to register SOP Generator: {e}")
            return False