#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Configuration Loader
Loads configuration from environment variables and config files.
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Config:
    """Configuration container"""
    gumroad_api_key: str = ""
    database_path: str = "./db/maha_sales_engine.db"
    api_key: str = ""
    encryption_key: str = ""
    log_level: str = "INFO"
    marketplace_db_url: str = "sqlite:///./db/marketplace_connector.db"
    webhook_secret: str = ""


class ConfigLoader:
    """Loads configuration from multiple sources"""
    
    def __init__(self, base_path: Optional[str] = None):
        # Default to project root (parent of maha-sales-engine)
        if base_path:
            self.base_path = Path(base_path)
        else:
            # config_loader is at: project/maha-sales-engine/marketplace_connector/config/config_loader.py
            # We want project root for .env and project/maha-sales-engine/config/engine.yaml
            self.base_path = Path(__file__).resolve().parent.parent.parent.parent
        self.config = Config()
        self._load_env()
        self._load_yaml()
    
    def _load_env(self):
        """Load from .env file"""
        env_file = self.base_path / ".env"
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ.setdefault(key.strip(), value.strip())
    
    def _load_yaml(self):
        """Load from engine.yaml"""
        # Try multiple possible locations
        possible_paths = [
            self.base_path / "maha-sales-engine" / "config" / "engine.yaml",
            self.base_path / "config" / "engine.yaml",
        ]
        
        yaml_file = None
        for path in possible_paths:
            if path.exists():
                yaml_file = path
                break
        
        if yaml_file:
            with open(yaml_file) as f:
                data = yaml.safe_load(f) or {}
                
                # Gumroad config
                marketplaces = data.get("marketplaces", {})
                gumroad = marketplaces.get("gumroad", {})
                if gumroad.get("api_key"):
                    self.config.gumroad_api_key = gumroad["api_key"]
                
                # Database config
                database = data.get("database", {})
                if database.get("path"):
                    self.config.database_path = database["path"]
                
                # Security config
                security = data.get("security", {})
                if security.get("api_key"):
                    self.config.api_key = security["api_key"]
                if security.get("encryption_key"):
                    self.config.encryption_key = security["encryption_key"]
                
                # Logging config
                logging_config = data.get("logging", {})
                if logging_config.get("level"):
                    self.config.log_level = logging_config["level"]
    
    def _load_env_vars(self):
        """Override with environment variables"""
        if os.getenv("GUMROAD_API_KEY"):
            self.config.gumroad_api_key = os.getenv("GUMROAD_API_KEY")
        if os.getenv("DATABASE_PATH"):
            self.config.database_path = os.getenv("DATABASE_PATH")
        if os.getenv("API_KEY"):
            self.config.api_key = os.getenv("API_KEY")
        if os.getenv("ENCRYPTION_KEY"):
            self.config.encryption_key = os.getenv("ENCRYPTION_KEY")
        if os.getenv("LOG_LEVEL"):
            self.config.log_level = os.getenv("LOG_LEVEL")
        if os.getenv("MARKETPLACE_DB_URL"):
            self.config.marketplace_db_url = os.getenv("MARKETPLACE_DB_URL")
        if os.getenv("WEBHOOK_SECRET"):
            self.config.webhook_secret = os.getenv("WEBHOOK_SECRET")
    
    def get_config(self) -> Config:
        """Get loaded configuration"""
        self._load_env_vars()
        return self.config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        config = self.get_config()
        return {
            "gumroad_api_key": config.gumroad_api_key,
            "database_path": config.database_path,
            "api_key": config.api_key,
            "encryption_key": config.encryption_key,
            "log_level": config.log_level,
            "marketplace_db_url": config.marketplace_db_url,
            "webhook_secret": config.webhook_secret
        }
    
    def validate(self) -> Dict[str, Any]:
        """Validate configuration"""
        config = self.get_config()
        errors = []
        warnings = []
        
        # Check Gumroad API key
        if not config.gumroad_api_key:
            errors.append("GUMROAD_API_KEY is required")
        
        # Check database path
        if not config.database_path:
            warnings.append("DATABASE_PATH not set, using default")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "config": {
                "gumroad_configured": bool(config.gumroad_api_key),
                "database_configured": bool(config.database_path),
                "api_key_configured": bool(config.api_key),
                "webhook_secret_configured": bool(config.webhook_secret)
            }
        }


def main():
    """Test configuration loading"""
    loader = ConfigLoader()
    config = loader.get_config()
    
    print("Configuration loaded:")
    print(f"  Gumroad API Key: {'***' + config.gumroad_api_key[-4:] if config.gumroad_api_key else 'NOT SET'}")
    print(f"  Database Path: {config.database_path}")
    print(f"  Log Level: {config.log_level}")
    
    validation = loader.validate()
    print(f"\nValidation: {'PASS' if validation['valid'] else 'FAIL'}")
    if validation['errors']:
        for error in validation['errors']:
            print(f"  ERROR: {error}")
    if validation['warnings']:
        for warning in validation['warnings']:
            print(f"  WARNING: {warning}")


if __name__ == "__main__":
    main()
