#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Main Entry Point
Windows Service Compatible
"""

import os
import sys
import time
import signal
import logging
from pathlib import Path
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.engine import CoreEngine, ConfigManager, DatabaseManager
from scheduler.scheduler import Scheduler, create_daily_outreach_job, create_daily_report_job, create_heartbeat_job, create_market_research_job, create_followup_job, create_backup_job
from products.product_manager import ProductManager
from market_intelligence.analyzer import MarketIntelligence
from marketplaces.manager import MarketplaceManager
from content.engine import ContentEngine
from analytics.engine import Analytics
from reporter.reporter import PerformanceReporter


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print(f"\nReceived signal {signum}, shutting down...")
    if 'engine' in globals():
        engine.stop()
    sys.exit(0)


def main():
    """Main entry point"""
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Initialize core engine
    engine = CoreEngine()
    
    # Initialize database
    db_path = Path(engine.config.get("database.path"))
    db = DatabaseManager(db_path)
    
    # Initialize modules
    product_manager = ProductManager(db)
    product_manager.initialize_default_products()
    
    market_intelligence = MarketIntelligence(engine.config, db)
    marketplace_manager = MarketplaceManager(engine.config, product_manager)
    marketplace_manager.initialize_default_listings()
    
    content_engine = ContentEngine(engine.config, product_manager)
    analytics = Analytics(engine.config, db)
    reporter = PerformanceReporter(engine.config, analytics, engine.health)
    scheduler = Scheduler()
    
    # Register modules with engine
    engine.register_module("products", product_manager)
    engine.register_module("market-intelligence", market_intelligence)
    engine.register_module("marketplaces", marketplace_manager)
    engine.register_module("content", content_engine)
    engine.register_module("analytics", analytics)
    engine.register_module("reporter", reporter)
    engine.register_module("scheduler", scheduler)
    
    # Register jobs
    # Note: We'll use placeholder functions for now
    # In production, these would be actual module methods
    
    # Start reporter
    reporter.start()
    
    # Start scheduler
    scheduler.start()
    
    # Run engine (blocks until shutdown)
    engine.run()


if __name__ == "__main__":
    main()
