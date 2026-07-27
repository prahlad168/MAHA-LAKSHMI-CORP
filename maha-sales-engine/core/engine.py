#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Core Engine
Responsibilities:
- Application lifecycle
- Configuration
- Dependency management
- Logging
- Health monitoring
"""

import os
import sys
import json
import time
import threading
import logging
import psutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from enum import Enum
import sqlite3
import yaml

# ============ CONFIGURATION ============

BASE_DIR = Path(__file__).parent.parent
CONFIG_FILE = BASE_DIR / "config" / "engine.yaml"
DB_FILE = BASE_DIR / "db" / "maha_sales_engine.db"
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Default configuration
DEFAULT_CONFIG = {
    "engine": {
        "name": "MAHA Sales Engine V1",
        "version": "1.0.0",
        "node_id": f"node-{os.getenv('COMPUTERNAME', 'unknown').lower()}",
        "environment": "production",
        "debug": False
    },
    "dashboard": {
        "url": "https://mahalaksmi.web.id",
        "api_endpoint": "/api/v1/sales-node/report",
        "heartbeat_interval": 60,
        "report_interval": 86400,
        "timeout": 30
    },
    "sales": {
        "daily_leads_target": 50,
        "daily_outreach_target": 100,
        "daily_revenue_target_usd": 100,
        "products": [
            "social-media-kit",
            "seo-bundle",
            "whatsapp-marketing",
            "landing-template",
            "business-kit"
        ]
    },
    "channels": {
        "email": {"enabled": True, "max_per_day": 30},
        "whatsapp": {"enabled": True, "max_per_day": 20},
        "linkedin": {"enabled": False, "max_per_day": 15}
    },
    "database": {
        "path": str(DB_FILE),
        "backup_interval": 86400,
        "retention_days": 90
    },
    "logging": {
        "level": "INFO",
        "max_size_mb": 10,
        "backup_count": 5,
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    },
    "security": {
        "api_key": "",
        "encryption_key": "",
        "cert_path": "",
        "key_path": "",
        "ca_path": ""
    }
}


class EngineState(Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class EngineStatus:
    """Engine status snapshot"""
    state: str
    uptime_seconds: float
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    active_modules: List[str]
    last_heartbeat: Optional[str]
    errors_count: int
    warnings_count: int


class ConfigManager:
    """Manage engine configuration"""
    
    def __init__(self, config_file: Path):
        self.config_file = config_file
        self.config = DEFAULT_CONFIG.copy()
        self.load()
    
    def load(self):
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    loaded = yaml.safe_load(f)
                self._deep_merge(self.config, loaded)
            except Exception as e:
                print(f"Warning: Failed to load config: {e}")
                self.save()
        else:
            self.save()
    
    def save(self):
        """Save configuration to file"""
        self.config_file.parent.mkdir(exist_ok=True)
        with open(self.config_file, "w") as f:
            yaml.dump(self.config, f, default_flow_style=False)
    
    def get(self, key_path: str, default=None):
        """Get config value by dot-separated path"""
        keys = key_path.split(".")
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def set(self, key_path: str, value: Any):
        """Set config value by dot-separated path"""
        keys = key_path.split(".")
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
        self.save()
    
    def _deep_merge(self, base: Dict, override: Dict):
        """Deep merge override into base"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value


class DatabaseManager:
    """Manage local SQLite database"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.connection = None
        self.initialize()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        if not self.connection:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def initialize(self):
        """Initialize database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                price_usd REAL,
                price_idr REAL,
                category TEXT,
                features TEXT,
                status TEXT DEFAULT 'active',
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        # Leads table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                company TEXT,
                industry TEXT,
                country TEXT,
                language TEXT,
                source TEXT,
                status TEXT DEFAULT 'new',
                score INTEGER DEFAULT 0,
                created_at TEXT,
                last_contact TEXT,
                followup_count INTEGER DEFAULT 0,
                notes TEXT
            )
        """)
        
        # Outreach log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS outreach_log (
                id TEXT PRIMARY KEY,
                lead_id TEXT,
                channel TEXT NOT NULL,
                template_type TEXT,
                content TEXT,
                status TEXT DEFAULT 'sent',
                sent_at TEXT,
                response_received INTEGER DEFAULT 0,
                response_at TEXT,
                FOREIGN KEY (lead_id) REFERENCES leads (id)
            )
        """)
        
        # Transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                gateway TEXT NOT NULL,
                customer_email TEXT,
                customer_name TEXT,
                amount REAL NOT NULL,
                currency TEXT NOT NULL,
                fee_amount REAL DEFAULT 0.0,
                net_amount REAL NOT NULL,
                product_id TEXT,
                status TEXT DEFAULT 'pending',
                payment_method TEXT,
                created_at TEXT,
                completed_at TEXT,
                metadata TEXT
            )
        """)
        
        # Reports table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                report_type TEXT NOT NULL,
                date TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TEXT
            )
        """)
        
        # System metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                cpu_usage REAL,
                memory_usage REAL,
                disk_usage REAL,
                active_leads INTEGER,
                queue_size INTEGER
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_reports_date ON reports(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON system_metrics(timestamp)")
        
        conn.commit()
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None


class HealthMonitor:
    """Monitor system and application health"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.errors_count = 0
        self.warnings_count = 0
        self.active_modules: List[str] = []
    
    def get_status(self) -> EngineStatus:
        """Get current engine status"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        try:
            cpu_usage = psutil.cpu_percent(interval=0.1)
            memory_usage = psutil.virtual_memory().percent
            disk_usage = psutil.disk_usage(str(BASE_DIR)).percent
        except Exception:
            cpu_usage = 0.0
            memory_usage = 0.0
            disk_usage = 0.0
        
        return EngineStatus(
            state=EngineState.RUNNING.value,
            uptime_seconds=uptime,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage,
            active_modules=self.active_modules,
            last_heartbeat=datetime.now().isoformat(),
            errors_count=self.errors_count,
            warnings_count=self.warnings_count
        )
    
    def increment_errors(self):
        """Increment error counter"""
        self.errors_count += 1
    
    def increment_warnings(self):
        """Increment warning counter"""
        self.warnings_count += 1
    
    def add_module(self, module_name: str):
        """Add active module"""
        if module_name not in self.active_modules:
            self.active_modules.append(module_name)


class CoreEngine:
    """Main engine orchestrator"""
    
    def __init__(self):
        self.config = ConfigManager(CONFIG_FILE)
        self.db = DatabaseManager(Path(self.config.get("database.path")))
        self.health = HealthMonitor()
        self.state = EngineState.INITIALIZING
        self.modules = {}
        self.threads = []
        self.logger = self._setup_logging()
        
        # Register core modules
        self.health.add_module("core")
        self.health.add_module("database")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("maha-sales-engine")
        logger.setLevel(logging.INFO)
        
        # File handler with rotation
        from logging.handlers import RotatingFileHandler
        fh = RotatingFileHandler(
            LOG_DIR / "engine.log",
            maxBytes=self.config.get("logging.max_size_mb", 10) * 1024 * 1024,
            backupCount=self.config.get("logging.backup_count", 5)
        )
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(self.config.get("logging.format"))
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    def register_module(self, name: str, module_instance):
        """Register a module with the engine"""
        self.modules[name] = module_instance
        self.health.add_module(name)
        self.logger.info(f"Module registered: {name}")
    
    def start(self):
        """Start the engine"""
        self.logger.info("=" * 60)
        self.logger.info("🚀 Starting MAHA SALES ENGINE V1")
        self.logger.info("=" * 60)
        self.logger.info(f"Node ID: {self.config.get('engine.node_id')}")
        self.logger.info(f"Dashboard: {self.config.get('dashboard.url')}")
        self.logger.info(f"Environment: {self.config.get('engine.environment')}")
        
        self.state = EngineState.RUNNING
        
        # Start all registered modules
        for name, module in self.modules.items():
            try:
                if hasattr(module, "start"):
                    module.start()
                self.logger.info(f"✅ Module started: {name}")
            except Exception as e:
                self.logger.error(f"❌ Failed to start module {name}: {e}")
                self.health.increment_errors()
        
        self.logger.info("=" * 60)
        self.logger.info("✅ MAHA SALES ENGINE V1 is running")
        self.logger.info("=" * 60)
    
    def stop(self):
        """Stop the engine"""
        self.logger.info("🛑 Shutting down MAHA SALES ENGINE V1")
        self.state = EngineState.STOPPED
        
        # Stop all modules
        for name, module in self.modules.items():
            try:
                if hasattr(module, "stop"):
                    module.stop()
                self.logger.info(f"✅ Module stopped: {name}")
            except Exception as e:
                self.logger.error(f"❌ Error stopping module {name}: {e}")
        
        # Close database
        self.db.close()
        
        self.logger.info("✅ Engine stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get engine status"""
        health_status = self.health.get_status()
        return {
            "engine": {
                "name": self.config.get("engine.name"),
                "version": self.config.get("engine.version"),
                "node_id": self.config.get("engine.node_id"),
                "state": self.state.value,
                "uptime": health_status.uptime_seconds
            },
            "health": asdict(health_status),
            "modules": {
                name: {
                    "status": "running" if name in self.health.active_modules else "stopped"
                }
                for name in self.modules.keys()
            },
            "dashboard": {
                "url": self.config.get("dashboard.url"),
                "last_heartbeat": health_status.last_heartbeat
            }
        }
    
    def run(self):
        """Main engine loop"""
        try:
            self.start()
            
            # Keep main thread alive
            while self.state == EngineState.RUNNING:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("Received shutdown signal")
        finally:
            self.stop()


def main():
    """Main entry point"""
    engine = CoreEngine()
    engine.run()


if __name__ == "__main__":
    main()
