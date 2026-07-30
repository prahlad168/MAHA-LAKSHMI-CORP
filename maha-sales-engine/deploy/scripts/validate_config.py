#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Production Configuration Validator

Validates production configuration before deployment.
"""

import sys
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.logging_utils import get_logger

logger = get_logger("deployment.config")


class ConfigValidator:
    """Validates production configuration"""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.errors = []
        self.warnings = []
    
    def validate(self) -> Dict[str, Any]:
        """Validate configuration"""
        if not self.config_path.exists():
            return {
                "valid": False,
                "errors": [f"Config file not found: {self.config_path}"],
                "warnings": []
            }
        
        try:
            import yaml
            with open(self.config_path) as f:
                config = yaml.safe_load(f)
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Failed to parse config: {e}"],
                "warnings": []
            }
        
        self._validate_required_sections(config)
        self._validate_database_config(config)
        self._validate_security_config(config)
        self._validate_api_config(config)
        
        return {
            "valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings
        }
    
    def _validate_required_sections(self, config: Dict[str, Any]) -> None:
        """Validate required configuration sections"""
        required_sections = ["engine", "database", "logging", "security"]
        for section in required_sections:
            if section not in config:
                self.errors.append(f"Missing required section: {section}")
    
    def _validate_database_config(self, config: Dict[str, Any]) -> None:
        """Validate database configuration"""
        db = config.get("database", {})
        
        if not db.get("url") and not db.get("path"):
            self.errors.append("Database configuration missing: url or path required")
        
        if db.get("pool_size", 10) < 1:
            self.errors.append("Database pool_size must be >= 1")
    
    def _validate_security_config(self, config: Dict[str, Any]) -> None:
        """Validate security configuration"""
        security = config.get("security", {})
        
        if not security.get("secret_key"):
            self.errors.append("Missing security.secret_key")
        elif security.get("secret_key") == "change-me-in-production-use-strong-secret":
            self.warnings.append("Using default secret_key - change in production")
        
        if not security.get("encryption_key"):
            self.errors.append("Missing security.encryption_key")
    
    def _validate_api_config(self, config: Dict[str, Any]) -> None:
        """Validate API configuration"""
        api = config.get("api", {})
        
        if api.get("workers", 1) < 1:
            self.errors.append("API workers must be >= 1")
        
        if api.get("timeout", 30) < 1:
            self.errors.append("API timeout must be >= 1")


def main():
    """CLI for configuration validator"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Production configuration validator")
    parser.add_argument("--config", default="config/engine.production.yaml", help="Config file path")
    
    args = parser.parse_args()
    
    validator = ConfigValidator(args.config)
    result = validator.validate()
    
    if result["valid"]:
        logger.info("Configuration is valid")
        if result["warnings"]:
            for warning in result["warnings"]:
                logger.warning(warning)
    else:
        logger.error("Configuration validation failed")
        for error in result["errors"]:
            logger.error(error)
        sys.exit(1)
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
