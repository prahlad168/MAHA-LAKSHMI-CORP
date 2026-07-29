#!/usr/bin/env python3
"""
MAHA LAKSHMI CORP - PostgreSQL Migration Rehearsal
Safe data-copy rehearsal from SQLite to PostgreSQL.
"""

import argparse
import logging
import os
import sqlite3
from datetime import datetime
from typing import List, Optional

logger = logging.getLogger(__name__)


def get_sqlite_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def get_postgres_connection(database_url: str):
    try:
        import psycopg2
        return psycopg2.connect(database_url)
    except ImportError:
        logger.error("psycopg2 is not installed. Install it with: pip install psycopg2-binary")
        raise
    except Exception as exc:
        logger.error("Failed to connect to PostgreSQL: %s", exc)
        raise


def get_tables(conn: sqlite3.Connection) -> List[str]:
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    )
    return [row[0] for row in cursor.fetchall()]


def copy_table(sqlite_conn: sqlite3.Connection, pg_conn, table: str, batch_size: int = 1000):
    cursor = sqlite_conn.execute(f"SELECT * FROM {table}")
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    if not rows:
        logger.info("Table %s: 0 rows", table)
        return

    placeholders = ", ".join(["%s"] * len(columns))
    column_list = ", ".join(columns)

    inserted = 0
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        with pg_conn.cursor() as pg_cursor:
            pg_cursor.executemany(
                f"INSERT INTO {table} ({column_list}) VALUES ({placeholders}) "
                f"ON CONFLICT DO NOTHING",
                [tuple(row) for row in batch],
            )
        pg_conn.commit()
        inserted += len(batch)
        logger.info("Table %s: inserted %d/%d rows", table, inserted, len(rows))

    logger.info("Table %s: complete (%d rows)", table, len(rows))


def rehearse(sqlite_path: str, database_url: str, tables: Optional[List[str]] = None):
    logger.info("PostgreSQL migration rehearsal started at %s", datetime.now().isoformat())
    logger.info("Source: %s", sqlite_path)
    logger.info("Target: %s", database_url)

    sqlite_conn = get_sqlite_connection(sqlite_path)
    pg_conn = get_postgres_connection(database_url)

    all_tables = get_tables(sqlite_conn)
    target_tables = tables or all_tables

    logger.info("Tables to migrate: %s", ", ".join(target_tables))

    for table in target_tables:
        if table not in all_tables:
            logger.warning("Table %s not found in SQLite; skipping", table)
            continue
        try:
            copy_table(sqlite_conn, pg_conn, table)
        except Exception as exc:
            logger.error("Failed to migrate table %s: %s", table, exc)
            raise

    sqlite_conn.close()
    pg_conn.close()
    logger.info("PostgreSQL migration rehearsal completed successfully at %s", datetime.now().isoformat())


def main():
    parser = argparse.ArgumentParser(description="PostgreSQL migration rehearsal")
    parser.add_argument("--sqlite-path", default=os.getenv("SQLITE_PATH", "./data/maha_lakshmi.db"))
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL"))
    parser.add_argument("--tables", nargs="*", help="Specific tables to migrate")
    args = parser.parse_args()

    if not args.database_url:
        logger.error("DATABASE_URL is required. Set it in environment or pass --database-url.")
        return 1

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        rehearse(args.sqlite_path, args.database_url, args.tables)
    except Exception as exc:
        logger.error("Migration rehearsal failed: %s", exc)
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
