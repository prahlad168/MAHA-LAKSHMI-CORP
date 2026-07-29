#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Shared Database Utilities
Connection pooling, query optimization, and database helpers.
"""

import os
import sys
import json
import time
import logging
import sqlite3
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from contextlib import contextmanager
from queue import Queue, Empty

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger("maha-sales-engine.shared.database")


class DatabaseError(Exception):
    """Database error"""
    pass


class ConnectionPool:
    """SQLite connection pool"""
    
    def __init__(self, database_path: str, max_connections: int = 10, timeout: int = 30):
        self.database_path = database_path
        self.max_connections = max_connections
        self.timeout = timeout
        self._pool: Queue = Queue(maxsize=max_connections)
        self._lock = threading.Lock()
        self._created_connections = 0
    
    def get_connection(self) -> sqlite3.Connection:
        """Get connection from pool"""
        try:
            # Try to get existing connection
            connection = self._pool.get_nowait()
            logger.debug("Reused connection from pool")
            return connection
        except Empty:
            pass
        
        # Create new connection
        with self._lock:
            if self._created_connections >= self.max_connections:
                # Wait for available connection
                try:
                    connection = self._pool.get(timeout=self.timeout)
                    logger.debug("Waited for connection from pool")
                    return connection
                except Empty:
                    raise DatabaseError("Connection pool exhausted")
            
            connection = self._create_connection()
            self._created_connections += 1
            logger.debug(f"Created new connection ({self._created_connections}/{self.max_connections})")
            return connection
    
    def return_connection(self, connection: sqlite3.Connection):
        """Return connection to pool"""
        try:
            self._pool.put_nowait(connection)
        except:
            # Pool is full, close connection
            connection.close()
            with self._lock:
                self._created_connections -= 1
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create new database connection"""
        conn = sqlite3.connect(
            self.database_path,
            check_same_thread=False,
            timeout=self.timeout
        )
        conn.row_factory = sqlite3.Row
        
        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=-64000")  # 64MB cache
        conn.execute("PRAGMA temp_store=MEMORY")
        conn.execute("PRAGMA mmap_size=268435456")  # 256MB mmap
        
        return conn
    
    def close_all(self):
        """Close all connections"""
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                conn.close()
            except Empty:
                break
        
        with self._lock:
            self._created_connections = 0


class DatabaseManager:
    """Enhanced database manager with connection pooling"""
    
    def __init__(self, database_path: str, pool_size: int = 10):
        self.database_path = str(Path(database_path).absolute())
        self.pool = ConnectionPool(self.database_path, max_connections=pool_size)
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Ensure database file exists"""
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self.database_path).touch(exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """Get database connection from pool"""
        conn = self.pool.get_connection()
        try:
            yield conn
        finally:
            self.pool.return_connection(conn)
    
    def execute(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute query and return results"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Database execute error: {e}")
            raise DatabaseError(f"Query failed: {e}")
    
    def execute_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Execute query and return single result"""
        results = self.execute(query, params)
        return results[0] if results else None
    
    def execute_many(self, query: str, params_list: List[tuple]):
        """Execute query with multiple parameter sets"""
        try:
            with self.get_connection() as conn:
                conn.executemany(query, params_list)
                conn.commit()
        except Exception as e:
            logger.error(f"Database execute_many error: {e}")
            raise DatabaseError(f"Batch query failed: {e}")
    
    def transaction(self, queries: List[tuple]):
        """Execute multiple queries in transaction"""
        try:
            with self.get_connection() as conn:
                for query, params in queries:
                    conn.execute(query, params)
                conn.commit()
        except Exception as e:
            logger.error(f"Transaction error: {e}")
            raise DatabaseError(f"Transaction failed: {e}")
    
    def create_tables(self, schema_sql: str):
        """Create tables from schema"""
        try:
            with self.get_connection() as conn:
                conn.executescript(schema_sql)
                conn.commit()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise DatabaseError(f"Schema creation failed: {e}")
    
    def close(self):
        """Close all connections"""
        self.pool.close_all()


class QueryBuilder:
    """SQL query builder"""
    
    def __init__(self, table: str):
        self.table = table
        self._conditions = []
        self._params = []
        self._order_by = ""
        self._limit = 0
        self._offset = 0
    
    def where(self, condition: str, params: Any = None):
        """Add WHERE condition"""
        if params is not None:
            self._conditions.append(condition)
            self._params.append(params)
        else:
            self._conditions.append(condition)
        return self
    
    def order_by(self, column: str, desc: bool = False):
        """Add ORDER BY"""
        direction = "DESC" if desc else "ASC"
        self._order_by = f"ORDER BY {column} {direction}"
        return self
    
    def limit(self, count: int, offset: int = 0):
        """Add LIMIT"""
        self._limit = count
        self._offset = offset
        return self
    
    def build_select(self, columns: str = "*") -> tuple:
        """Build SELECT query"""
        query = f"SELECT {columns} FROM {self.table}"
        
        if self._conditions:
            query += " WHERE " + " AND ".join(self._conditions)
        
        if self._order_by:
            query += f" {self._order_by}"
        
        if self._limit:
            query += f" LIMIT {self._limit} OFFSET {self._offset}"
        
        return query, self._params
    
    def build_delete(self) -> tuple:
        """Build DELETE query"""
        query = f"DELETE FROM {self.table}"
        
        if self._conditions:
            query += " WHERE " + " AND ".join(self._conditions)
        
        return query, self._params


def main():
    """Test database utilities"""
    import tempfile
    
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    try:
        db = DatabaseManager(db_path)
        
        # Test connection
        with db.get_connection() as conn:
            result = conn.execute("SELECT 1").fetchone()
            assert result[0] == 1
        
        # Test query builder
        builder = QueryBuilder("users")
        builder.where("id = ?", "123").where("active = ?", 1)
        query, params = builder.build_select()
        
        assert "WHERE" in query
        assert len(params) == 2
        
        db.close()
        print("Database utilities tests passed")
    finally:
        Path(db_path).unlink(missing_ok=True)


if __name__ == "__main__":
    main()
