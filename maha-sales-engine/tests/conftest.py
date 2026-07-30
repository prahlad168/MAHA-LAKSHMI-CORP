import os
import sys
import json
import pytest
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="function")
def temp_dir():
    """Create temporary directory for each test"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
    except:
        pass


@pytest.fixture(scope="function")
def db_manager(temp_dir):
    """Create database manager for each test"""
    from shared.database import DatabaseManager
    db_path = temp_dir / "test.db"
    db = DatabaseManager(db_path)
    yield db
    try:
        db.close()
    except:
        pass


@pytest.fixture
def sample_schema():
    """Sample validation schema"""
    return {
        "email": {"type": "email", "required": True},
        "name": {"type": "string", "required": True, "max_length": 100, "min_length": 2},
        "age": {"type": "integer", "min_value": 0, "max_value": 150},
        "price": {"type": "float", "min_value": 0.0},
        "status": {"type": "enum", "values": ["active", "inactive", "pending"]},
        "tags": {"type": "list", "max_items": 10},
        "metadata": {"type": "dict"}
    }
