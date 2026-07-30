#!/usr/bin/env python3
"""
MAHA Sales Engine V1 - Mission Control Tests

Test suite for the Mission Control system.
"""

import sys
import os
import pytest
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.database import DatabaseManager
from shared.auth import AuthManager
from mission_control.models import MissionContext, MissionConfig, MissionStatus, PermissionLevel, MissionMetric, MissionAlert
from mission_control.core.mission_controller import MissionController
from mission_control.permissions.permission_manager import PermissionManager
from mission_control.services.mission_service import MissionService
from mission_control.repositories.mission_repository import MissionRepository, MissionRecord


# Test fixtures
@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    import tempfile
    db_path = tempfile.mktemp(suffix=".db")
    db_manager = DatabaseManager(db_path)
    yield db_manager
    db_manager.close()
    try:
        os.unlink(db_path)
    except FileNotFoundError:
        pass


@pytest.fixture
def auth_manager(temp_db):
    """Create auth manager for testing"""
    return AuthManager(temp_db)


@pytest.fixture
def mission_config():
    """Create test mission configuration"""
    return MissionConfig(
        mission_id="test-mission-001",
        name="Test Mission",
        description="Test mission for unit testing",
        version="1.0.0",
        enabled=True,
        max_concurrent_operations=5,
        timeout_seconds=10,
        retry_attempts=2,
        retry_delay_seconds=1
    )


@pytest.fixture
def mission_context():
    """Create test mission context"""
    return MissionContext(
        mission_id="test-mission-001",
        user_id="test-user-001",
        permission_level=PermissionLevel.ADMIN,
        session_id="test-session-001",
        metadata={"permissions": ["read", "write", "admin"]}
    )


class TestMissionConfig:
    """Test MissionConfig model"""
    
    def test_config_creation(self):
        """Test mission config creation"""
        config = MissionConfig(
            mission_id="test-001",
            name="Test Mission",
            description="Test description"
        )
        assert config.mission_id == "test-001"
        assert config.name == "Test Mission"
        assert config.version == "1.0.0"
        assert config.enabled is True
    
    def test_config_to_dict(self):
        """Test config serialization"""
        config = MissionConfig(
            mission_id="test-001",
            name="Test Mission",
            description="Test description"
        )
        config_dict = config.to_dict()
        assert config_dict["mission_id"] == "test-001"
        assert config_dict["name"] == "Test Mission"
        assert "version" in config_dict
    
    def test_config_from_dict(self):
        """Test config deserialization"""
        data = {
            "mission_id": "test-001",
            "name": "Test Mission",
            "description": "Test description",
            "version": "2.0.0"
        }
        config = MissionConfig.from_dict(data)
        assert config.mission_id == "test-001"
        assert config.version == "2.0.0"


class TestMissionContext:
    """Test MissionContext model"""
    
    def test_context_creation(self):
        """Test mission context creation"""
        context = MissionContext(
            mission_id="mission-001",
            user_id="user-001",
            permission_level=PermissionLevel.ADMIN
        )
        assert context.mission_id == "mission-001"
        assert context.user_id == "user-001"
        assert context.permission_level == PermissionLevel.ADMIN
    
    def test_context_to_dict(self):
        """Test context serialization"""
        context = MissionContext(
            mission_id="mission-001",
            user_id="user-001",
            permission_level=PermissionLevel.CEO
        )
        context_dict = context.to_dict()
        assert context_dict["mission_id"] == "mission-001"
        assert context_dict["permission_level"] == "ceo"
    
    def test_context_from_dict(self):
        """Test context deserialization"""
        data = {
            "mission_id": "mission-001",
            "user_id": "user-001",
            "permission_level": "operator",
            "session_id": "session-001"
        }
        context = MissionContext.from_dict(data)
        assert context.mission_id == "mission-001"
        assert context.permission_level == PermissionLevel.OPERATOR
        assert context.session_id == "session-001"


class TestMissionRepository:
    """Test MissionRepository"""
    
    def test_create_mission(self, temp_db):
        """Test creating a mission"""
        repo = MissionRepository(temp_db)
        mission = MissionRecord(
            mission_id="test-mission-001",
            name="Test Mission",
            status="pending",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            config={"test": "config"}
        )
        assert repo.create_mission(mission) is True
    
    def test_get_mission(self, temp_db):
        """Test getting a mission"""
        repo = MissionRepository(temp_db)
        mission = MissionRecord(
            mission_id="test-mission-002",
            name="Test Mission 2",
            status="running",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            config={"test": "config"}
        )
        repo.create_mission(mission)
        retrieved = repo.get_mission("test-mission-002")
        assert retrieved is not None
        assert retrieved.name == "Test Mission 2"
    
    def test_list_missions(self, temp_db):
        """Test listing missions"""
        repo = MissionRepository(temp_db)
        for i in range(3):
            mission = MissionRecord(
                mission_id=f"test-mission-{i:03d}",
                name=f"Test Mission {i}",
                status="pending",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                config={"test": "config"}
            )
            repo.create_mission(mission)
        
        missions = repo.list_missions(limit=10)
        assert len(missions) == 3


class TestMissionService:
    """Test MissionService"""
    
    def test_service_initialization(self, mission_config, auth_manager):
        """Test service initialization"""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        from shared.database import DatabaseManager
        db_manager = DatabaseManager(db_path)
        service = MissionService(mission_config, db_manager, auth_manager)
        assert service.config == mission_config
        assert service.db is not None
        assert service.auth is not None
        db_manager.close()
        os.unlink(db_path)
    
    def test_create_mission(self, mission_config, auth_manager, mission_context):
        """Test mission creation through service"""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        from shared.database import DatabaseManager
        db_manager = DatabaseManager(db_path)
        service = MissionService(mission_config, db_manager, auth_manager)
        
        result = service.create_mission(mission_context, {"name": "Test Mission"})
        assert result["mission_id"] == mission_context.mission_id
        assert result["status"] == MissionStatus.INITIALIZING.value
        db_manager.close()
        os.unlink(db_path)


class TestPermissionManager:
    """Test PermissionManager"""
    
    def test_permission_check_ceo(self, auth_manager):
        """Test CEO permissions"""
        perm_mgr = PermissionManager(auth_manager)
        assert perm_mgr.check_permission("ceo", "mission", "read") is True
        assert perm_mgr.check_permission("ceo", "mission", "delete") is True
    
    def test_permission_check_viewer(self, auth_manager):
        """Test viewer permissions"""
        perm_mgr = PermissionManager(auth_manager)
        assert perm_mgr.check_permission("viewer", "mission", "read") is True
        assert perm_mgr.check_permission("viewer", "mission", "write") is False
        assert perm_mgr.check_permission("viewer", "mission", "delete") is False
    
    def test_permission_check_operator(self, auth_manager):
        """Test operator permissions"""
        perm_mgr = PermissionManager(auth_manager)
        assert perm_mgr.check_permission("operator", "mission", "read") is True
        assert perm_mgr.check_permission("operator", "mission", "update") is True
        assert perm_mgr.check_permission("operator", "mission", "delete") is False
    
    def test_get_user_permissions(self, auth_manager):
        """Test getting user permissions"""
        perm_mgr = PermissionManager(auth_manager)
        ceo_perms = perm_mgr.get_user_permissions("ceo")
        assert "mission:read" in ceo_perms
        assert "mission:write" not in ceo_perms
        assert "mission:create" in ceo_perms
        assert "mission:delete" in ceo_perms


class TestMissionController:
    """Test MissionController"""
    
    def test_controller_initialization(self):
        """Test controller initialization"""
        controller = MissionController()
        assert controller.config is not None
        assert controller.db is not None
        assert controller.auth is not None
        assert controller.service is not None
    
    def test_get_system_health(self):
        """Test getting system health"""
        controller = MissionController()
        health = controller.get_system_health()
        assert "status" in health
        assert "timestamp" in health
        assert "services" in health
    
    def test_get_controller_metrics(self):
        """Test getting controller metrics"""
        controller = MissionController()
        metrics = controller.get_controller_metrics()
        assert "uptime_seconds" in metrics
        assert "operations_processed" in metrics
        assert "active_missions" in metrics


class TestMissionRouter:
    """Test MissionRouter"""
    
    def test_router_initialization(self):
        """Test router initialization"""
        controller = MissionController()
        from mission_control.api.mission_router import create_mission_router
        router = create_mission_router(controller)
        assert router is not None
        assert router.controller is not None
    
    def test_health_endpoint(self):
        """Test health endpoint exists"""
        controller = MissionController()
        from mission_control.api.mission_router import create_mission_router
        router = create_mission_router(controller)
        
        # Check if routes are registered
        routes = [route.path for route in router.app.routes]
        assert "/mission/status" in routes
        assert "/mission/info" in routes
        assert "/mission/version" in routes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
