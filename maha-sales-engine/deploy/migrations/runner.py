#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Database Migration Runner

Handles database schema migrations for production deployments.
"""

import sys
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.database import DatabaseManager
from shared.logging_utils import get_logger

logger = get_logger("deployment.migrations")


class Migration:
    """Database migration definition"""
    
    def __init__(self, version: str, name: str, up_sql: str, down_sql: str = ""):
        self.version = version
        self.name = name
        self.up_sql = up_sql
        self.down_sql = down_sql
        self.applied_at: Optional[str] = None


class MigrationRunner:
    """Runs database migrations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.migrations: List[Migration] = []
        self._ensure_migration_table()
    
    def _ensure_migration_table(self):
        """Create migration tracking table if it doesn't exist"""
        try:
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    applied_at TEXT NOT NULL
                )
            """)
            logger.info("Migration table created/verified")
        except Exception as e:
            logger.error(f"Failed to create migration table: {e}")
            raise
    
    def register_migration(self, migration: Migration) -> None:
        """Register a migration"""
        self.migrations.append(migration)
        logger.info(f"Migration registered: {migration.version} - {migration.name}")
    
    def run_migrations(self) -> Dict[str, Any]:
        """Run all pending migrations"""
        results = {
            "applied": [],
            "skipped": [],
            "failed": []
        }
        
        for migration in sorted(self.migrations, key=lambda m: m.version):
            try:
                if self._is_applied(migration.version):
                    results["skipped"].append(migration.version)
                    continue
                
                self._apply_migration(migration)
                results["applied"].append(migration.version)
                logger.info(f"Migration applied: {migration.version} - {migration.name}")
            except Exception as e:
                results["failed"].append({
                    "version": migration.version,
                    "error": str(e)
                })
                logger.error(f"Migration failed: {migration.version} - {e}")
        
        return results
    
    def _is_applied(self, version: str) -> bool:
        """Check if migration has been applied"""
        try:
            result = self.db.execute(
                "SELECT COUNT(*) FROM schema_migrations WHERE version = ?",
                (version,)
            )
            return result[0]["COUNT(*)"] > 0 if result else False
        except Exception:
            return False
    
    def _apply_migration(self, migration: Migration) -> None:
        """Apply a single migration"""
        try:
            self.db.execute(migration.up_sql)
            self.db.execute(
                "INSERT INTO schema_migrations (version, name, applied_at) VALUES (?, ?, ?)",
                (migration.version, migration.name, datetime.now().isoformat())
            )
        except Exception as e:
            logger.error(f"Failed to apply migration {migration.version}: {e}")
            raise
    
    def rollback(self, target_version: str) -> Dict[str, Any]:
        """Rollback migrations to target version"""
        results = {
            "rolled_back": []
        }
        
        for migration in reversed(sorted(self.migrations, key=lambda m: m.version)):
            if migration.version <= target_version:
                break
            
            try:
                if self._is_applied(migration.version) and migration.down_sql:
                    self.db.execute(migration.down_sql)
                    self.db.execute(
                        "DELETE FROM schema_migrations WHERE version = ?",
                        (migration.version,)
                    )
                    results["rolled_back"].append(migration.version)
                    logger.info(f"Migration rolled back: {migration.version}")
            except Exception as e:
                logger.error(f"Failed to rollback migration {migration.version}: {e}")
        
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """Get migration status"""
        try:
            applied = self.db.execute("SELECT version, name, applied_at FROM schema_migrations ORDER BY version")
            return {
                "applied_migrations": [dict(row) for row in applied] if applied else [],
                "pending_migrations": [m.version for m in self.migrations if not self._is_applied(m.version)]
            }
        except Exception as e:
            return {"error": str(e)}


def create_default_migrations() -> List[Migration]:
    """Create default database migrations"""
    return [
        Migration(
            version="001",
            name="initial_schema",
            up_sql="""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    applied_at TEXT NOT NULL
                );
            """,
            down_sql="DROP TABLE IF EXISTS schema_migrations;"
        ),
        Migration(
            version="002",
            name="create_mission_control_tables",
            up_sql="""
                CREATE TABLE IF NOT EXISTS missions (
                    mission_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    config TEXT NOT NULL,
                    result TEXT
                );
                
                CREATE TABLE IF NOT EXISTS mission_metrics (
                    metric_id TEXT PRIMARY KEY,
                    mission_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    tags TEXT,
                    FOREIGN KEY (mission_id) REFERENCES missions (mission_id)
                );
                
                CREATE TABLE IF NOT EXISTS mission_alerts (
                    alert_id TEXT PRIMARY KEY,
                    mission_id TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    source TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    acknowledged INTEGER DEFAULT 0,
                    metadata TEXT,
                    FOREIGN KEY (mission_id) REFERENCES missions (mission_id)
                );
                
                CREATE TABLE IF NOT EXISTS mission_audit (
                    audit_id TEXT PRIMARY KEY,
                    mission_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    details TEXT,
                    FOREIGN KEY (mission_id) REFERENCES missions (mission_id)
                );
            """,
            down_sql="""
                DROP TABLE IF EXISTS mission_audit;
                DROP TABLE IF EXISTS mission_alerts;
                DROP TABLE IF EXISTS mission_metrics;
                DROP TABLE IF EXISTS missions;
            """
        ),
        Migration(
            version="003",
            name="create_indexes",
            up_sql="""
                CREATE INDEX IF NOT EXISTS idx_missions_status ON missions(status);
                CREATE INDEX IF NOT EXISTS idx_missions_created ON missions(created_at);
                CREATE INDEX IF NOT EXISTS idx_metrics_mission ON mission_metrics(mission_id);
                CREATE INDEX IF NOT EXISTS idx_alerts_mission ON mission_alerts(mission_id);
                CREATE INDEX IF NOT EXISTS idx_audit_mission ON mission_audit(mission_id);
            """,
            down_sql="""
                DROP INDEX IF EXISTS idx_missions_status;
                DROP INDEX IF EXISTS idx_missions_created;
                DROP INDEX IF EXISTS idx_metrics_mission;
                DROP INDEX IF EXISTS idx_alerts_mission;
                DROP INDEX IF EXISTS idx_audit_mission;
            """
        )
    ]


def main():
    """Run database migrations"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database migration runner")
    parser.add_argument("--db", default="data/maha.db", help="Database path")
    parser.add_argument("--rollback", help="Rollback to version")
    parser.add_argument("--status", action="store_true", help="Show migration status")
    
    args = parser.parse_args()
    
    db_manager = DatabaseManager(args.db)
    runner = MigrationRunner(db_manager)
    
    # Register default migrations
    for migration in create_default_migrations():
        runner.register_migration(migration)
    
    if args.status:
        status = runner.get_status()
        print(json.dumps(status, indent=2))
    elif args.rollback:
        result = runner.rollback(args.rollback)
        print(json.dumps(result, indent=2))
    else:
        result = runner.run_migrations()
        print(json.dumps(result, indent=2))
    
    db_manager.close()


if __name__ == "__main__":
    main()
