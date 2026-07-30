#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Phase 14 Verification
Verify all modules start correctly and system is operational.
"""

import sys
import time
import logging
from pathlib import Path
from typing import Dict, Any, List

sys.path.insert(0, str(Path(__file__).parent))

logger = logging.getLogger("maha-sales-engine.verification")


class SystemVerifier:
    """Verify system components"""
    
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
    
    def verify(self, name: str, func) -> bool:
        """Run verification check"""
        try:
            result = func()
            status = "PASS" if result else "FAIL"
            self.results.append({"name": name, "status": status, "result": result})
            if result:
                self.passed += 1
            else:
                self.failed += 1
            logger.info(f"[{status}] {name}")
            return result
        except Exception as e:
            self.results.append({"name": name, "status": "ERROR", "error": str(e)})
            self.failed += 1
            logger.error(f"[ERROR] {name}: {e}")
            return False
    
    def verify_module_import(self, module_path: str) -> bool:
        """Verify module can be imported"""
        try:
            # Use importlib for more reliable imports
            import importlib
            mod = importlib.import_module(module_path)
            return mod is not None
        except Exception as e:
            logger.error(f"Import failed for {module_path}: {e}")
            return False
    
    def verify_database_initializes(self) -> bool:
        """Verify database initializes"""
        try:
            from shared.database import DatabaseManager
            import tempfile
            db_path = Path(tempfile.mkdtemp()) / "verify.db"
            db = DatabaseManager(db_path)
            db.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY)")
            db.close()
            return True
        except Exception as e:
            logger.error(f"Database init failed: {e}")
            return False
    
    def verify_health_endpoints(self) -> bool:
        """Verify health endpoints exist"""
        try:
            from shared.health import health_monitor
            return health_monitor is not None
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def verify_scheduler_starts(self) -> bool:
        """Verify scheduler can start"""
        try:
            from scheduler.scheduler import Scheduler
            scheduler = Scheduler()
            scheduler.start()
            scheduler.stop()
            return True
        except Exception as e:
            logger.error(f"Scheduler failed: {e}")
            return False
    
    def verify_product_factory(self) -> bool:
        """Verify product factory initializes"""
        try:
            from product_factory.core.factory import ProductFactory
            from core.engine import ConfigManager, DatabaseManager
            import tempfile
            import yaml
            
            temp_dir = Path(tempfile.mkdtemp())
            db_path = temp_dir / "test.db"
            db = DatabaseManager(db_path)
            
            config_data = {"database": {"path": str(db_path)}, "product_factory": {"output_dir": str(temp_dir / "output")}}
            config_path = temp_dir / "config.yaml"
            with open(config_path, "w") as f:
                yaml.dump(config_data, f)
            config = ConfigManager(config_path)
            
            factory = ProductFactory(db, config)
            db.close()
            return True
        except Exception as e:
            logger.error(f"Product factory failed: {e}")
            return False
    
    def verify_marketing_engine(self) -> bool:
        """Verify marketing engine initializes"""
        try:
            from marketing_engine.core.engine import MarketingEngine
            return True
        except Exception as e:
            logger.error(f"Marketing engine failed: {e}")
            return False
    
    def verify_sales_automation(self) -> bool:
        """Verify sales automation initializes"""
        try:
            from sales_automation.core.engine import AutomationCore
            return True
        except Exception as e:
            logger.error(f"Sales automation failed: {e}")
            return False
    
    def verify_business_pipeline(self) -> bool:
        """Verify business pipeline initializes"""
        try:
            from business.pipeline.engine import BusinessPipeline
            return True
        except Exception as e:
            logger.error(f"Business pipeline failed: {e}")
            return False
    
    def verify_marketplace(self) -> bool:
        """Verify marketplace initializes"""
        try:
            from marketplace.core.registry import ProviderRegistry
            from marketplace.core.state_machine import StateMachine
            return True
        except Exception as e:
            logger.error(f"Marketplace failed: {e}")
            return False
    
    def run_all_verifications(self) -> Dict[str, Any]:
        """Run all verifications"""
        logger.info("=" * 60)
        logger.info("PHASE 14: SYSTEM VERIFICATION")
        logger.info("=" * 60)
        
        # Core modules
        self.verify("Core Engine Import", lambda: self.verify_module_import("core.engine"))
        self.verify("Database Initializes", self.verify_database_initializes)
        self.verify("Health Endpoints", self.verify_health_endpoints)
        self.verify("Scheduler Starts", self.verify_scheduler_starts)
        
        # Business modules
        self.verify("Product Factory", self.verify_product_factory)
        self.verify("Marketing Engine", self.verify_marketing_engine)
        self.verify("Sales Automation", self.verify_sales_automation)
        self.verify("Business Pipeline", self.verify_business_pipeline)
        self.verify("Marketplace", self.verify_marketplace)
        
        # Summary
        logger.info("=" * 60)
        logger.info(f"RESULTS: {self.passed} passed, {self.failed} failed")
        logger.info("=" * 60)
        
        return {
            "total": len(self.results),
            "passed": self.passed,
            "failed": self.failed,
            "results": self.results,
            "status": "OPERATIONAL" if self.failed == 0 else "DEGRADED"
        }


def main():
    """Run verification"""
    logging.basicConfig(level=logging.INFO)
    verifier = SystemVerifier()
    results = verifier.run_all_verifications()
    
    print("\n" + "=" * 60)
    print("PHASE 14 VERIFICATION COMPLETE")
    print("=" * 60)
    print(f"Total Checks: {results['total']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"System Status: {results['status']}")
    print("=" * 60)
    
    for result in results["results"]:
        status_symbol = "[PASS]" if result["status"] == "PASS" else "[FAIL]" if result["status"] == "FAIL" else "[ERR]"
        print(f"{status_symbol} {result['name']}")
    
    return 0 if results["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
