"""
MAHA LAKSHMI CORP - Database Connection and Migration Manager
Production-grade database setup with migrations.
"""

import sqlite3
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Database path
DB_PATH = Path(__file__).parent.parent.parent / "data" / "maha_lakshmi.db"
DB_PATH.parent.mkdir(exist_ok=True)

# Migration directory
MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def get_connection() -> sqlite3.Connection:
    """Get database connection with optimized settings"""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA cache_size=-64000")  # 64MB cache
    conn.execute("PRAGMA mmap_size=268435456")  # 256MB mmap
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA temp_store=MEMORY")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Initialize database with migrations"""
    conn = get_connection()
    try:
        # Create migration tracking table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TEXT NOT NULL,
                description TEXT
            )
        """)
        
        # Get applied migrations
        cursor = conn.execute("SELECT version FROM schema_migrations ORDER BY version")
        applied = {row[0] for row in cursor.fetchall()}
        
        # Apply pending migrations
        migrations = sorted(MIGRATIONS_DIR.glob("*.sql"))
        for migration_file in migrations:
            version = migration_file.stem
            if version not in applied:
                apply_migration(conn, migration_file, version)
        
        conn.commit()
        logger.info(f"Database initialized with {len(applied)} migrations applied")
    finally:
        conn.close()


def apply_migration(conn: sqlite3.Connection, migration_file: Path, version: str):
    """Apply a single migration"""
    try:
        sql = migration_file.read_text()
        conn.executescript(sql)
        
        # Record migration
        conn.execute(
            "INSERT INTO schema_migrations (version, applied_at, description) VALUES (?, ?, ?)",
            (version, datetime.now().isoformat(), migration_file.stem)
        )
        
        logger.info(f"Applied migration: {version}")
    except Exception as e:
        logger.error(f"Failed to apply migration {version}: {e}")
        raise


def get_db() -> sqlite3.Connection:
    """FastAPI dependency for database connection"""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


# Database helper functions
def execute_query(query: str, params: tuple = None, fetch: str = "all") -> Any:
    """Execute a database query"""
    conn = get_connection()
    try:
        cursor = conn.execute(query, params or ())
        if fetch == "all":
            return [dict(row) for row in cursor.fetchall()]
        elif fetch == "one":
            row = cursor.fetchone()
            return dict(row) if row else None
        elif fetch == "none":
            conn.commit()
            return None
    finally:
        conn.close()


def execute_many(query: str, params_list: List[tuple]) -> None:
    """Execute many queries"""
    conn = get_connection()
    try:
        conn.executemany(query, params_list)
        conn.commit()
    finally:
        conn.close()


def transaction(func):
    """Decorator for database transactions"""
    def wrapper(*args, **kwargs):
        conn = get_connection()
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()
    return wrapper
