#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Shared Test Infrastructure
Common test utilities and base classes.
"""

import os
import sys
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class BaseTestCase:
    """Base test case with common utilities"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def db_manager(self, temp_dir):
        """Create database manager"""
        from shared.database import DatabaseManager
        db_path = temp_dir / "test.db"
        return DatabaseManager(db_path)
    
    @pytest.fixture
    def mock_event_bus(self):
        """Create mock event bus"""
        return Mock()
    
    def assert_response(self, response, expected_status: int, expected_keys: List[str] = None):
        """Assert response structure"""
        assert response.status_code == expected_status
        if expected_keys:
            data = response.json()
            for key in expected_keys:
                assert key in data
    
    def assert_error_response(self, response, expected_code: str):
        """Assert error response"""
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == expected_code


class APITestCase(BaseTestCase):
    """Base test case for API tests"""
    
    @pytest.fixture
    def client(self, db_manager):
        """Create test client"""
        from fastapi.testclient import TestClient
        # Import app based on module
        return None
    
    def get_auth_headers(self, api_key: str) -> Dict[str, str]:
        """Get authorization headers"""
        return {"X-API-Key": api_key}
    
    def post_json(self, client, url: str, data: Dict, headers: Dict = None) -> Any:
        """Helper for POST requests"""
        import json
        headers = headers or {}
        headers.setdefault("Content-Type", "application/json")
        return client.post(url, data=json.dumps(data), headers=headers)
    
    def get_json(self, client, url: str, headers: Dict = None) -> Any:
        """Helper for GET requests"""
        return client.get(url, headers=headers)


class DatabaseTestCase(BaseTestCase):
    """Base test case for database tests"""
    
    def insert_test_data(self, db_manager, table: str, data: Dict):
        """Insert test data"""
        columns = list(data.keys())
        placeholders = ["?" for _ in columns]
        values = list(data.values())
        
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        db_manager.execute(query, tuple(values))
    
    def get_test_data(self, db_manager, table: str, filters: Dict = None) -> List[Dict]:
        """Get test data"""
        query = f"SELECT * FROM {table}"
        params = []
        
        if filters:
            conditions = [f"{k} = ?" for k in filters.keys()]
            query += " WHERE " + " AND ".join(conditions)
            params = list(filters.values())
        
        return db_manager.execute(query, tuple(params))


def main():
    """Test infrastructure"""
    print("Test infrastructure loaded")


if __name__ == "__main__":
    main()
