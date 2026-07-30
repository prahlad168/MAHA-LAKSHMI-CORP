#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Production Deployment Tests

Tests for production deployment components.
"""

import sys
import os
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from deploy.startup import StartupValidator, GracefulShutdown
from deploy.health import HealthCheckServer, check_health
from deploy.migrations.runner import MigrationRunner, Migration, create_default_migrations
from deploy.scripts.deploy import DeploymentScripts, DeploymentResult
from deploy.scripts.validate_config import ConfigValidator
from deploy.rollback import RollbackManager, RollbackPlan


class TestStartupValidator:
    """Test StartupValidator"""
    
    def test_validate_directories(self, tmp_path):
        """Test directory validation"""
        validator = StartupValidator()
        
        with patch('deploy.startup.Path') as mock_path:
            mock_path.return_value.exists.return_value = True
            assert validator._check_directories() is True
    
    def test_validate_environment(self, monkeypatch):
        """Test environment validation"""
        validator = StartupValidator()
        monkeypatch.setenv("MAHA_ENV", "production")
        assert validator._check_environment() is True
    
    def test_validate_all(self, monkeypatch, tmp_path):
        """Test full validation"""
        validator = StartupValidator()
        monkeypatch.setenv("MAHA_ENV", "production")
        
        with patch('deploy.startup.DatabaseManager') as mock_db:
            mock_db.return_value.execute.return_value = None
            mock_db.return_value.close.return_value = None
            result = validator.validate_all()
            assert isinstance(result, bool)


class TestGracefulShutdown:
    """Test GracefulShutdown"""
    
    def test_setup_signal_handlers(self):
        """Test signal handler setup"""
        shutdown = GracefulShutdown()
        shutdown.setup()
        assert shutdown.force_shutdown is False
    
    def test_shutdown(self):
        """Test shutdown procedure"""
        shutdown = GracefulShutdown()
        mock_app = MagicMock()
        mock_app.engine = MagicMock()
        mock_app.db = MagicMock()
        mock_app.cache = MagicMock()
        
        result = shutdown.shutdown(mock_app)
        assert result is True
        mock_app.engine.stop.assert_called_once()
        mock_app.db.close.assert_called_once()


class TestHealthCheckServer:
    """Test HealthCheckServer"""
    
    def test_check_health_function(self):
        """Test check_health function"""
        with patch('deploy.health.get_engine') as mock_engine:
            mock_engine.return_value.get_health.return_value = {"status": "running"}
            result = check_health()
            assert result["status"] == "healthy"
    
    def test_health_server_initialization(self):
        """Test health server initialization"""
        server = HealthCheckServer(host="127.0.0.1", port=8888)
        assert server.host == "127.0.0.1"
        assert server.port == 8888


class TestMigrationRunner:
    """Test MigrationRunner"""
    
    def test_ensure_migration_table(self, tmp_path):
        """Test migration table creation"""
        db_path = str(tmp_path / "test.db")
        from shared.database import DatabaseManager
        db = DatabaseManager(db_path)
        runner = MigrationRunner(db)
        
        result = db.execute("SELECT COUNT(*) FROM schema_migrations")
        assert result[0]["COUNT(*)"] == 0
        db.close()
    
    def test_register_migration(self, tmp_path):
        """Test migration registration"""
        db_path = str(tmp_path / "test.db")
        from shared.database import DatabaseManager
        db = DatabaseManager(db_path)
        runner = MigrationRunner(db)
        
        migration = Migration("001", "test", "CREATE TABLE test (id TEXT PRIMARY KEY);")
        runner.register_migration(migration)
        
        assert len(runner.migrations) == 1
        assert runner.migrations[0].version == "001"
        db.close()
    
    def test_run_migrations(self, tmp_path):
        """Test running migrations"""
        db_path = str(tmp_path / "test.db")
        from shared.database import DatabaseManager
        db = DatabaseManager(db_path)
        runner = MigrationRunner(db)
        
        migration = Migration("001", "test", "CREATE TABLE test (id TEXT PRIMARY KEY);")
        runner.register_migration(migration)
        
        result = runner.run_migrations()
        assert len(result["applied"]) == 1
        assert "001" in result["applied"]
        db.close()
    
    def test_get_status(self, tmp_path):
        """Test migration status"""
        db_path = str(tmp_path / "test.db")
        from shared.database import DatabaseManager
        db = DatabaseManager(db_path)
        runner = MigrationRunner(db)
        
        status = runner.get_status()
        assert "applied_migrations" in status
        assert "pending_migrations" in status
        db.close()
    
    def test_default_migrations(self):
        """Test default migrations creation"""
        migrations = create_default_migrations()
        assert len(migrations) >= 2
        versions = [m.version for m in migrations]
        assert "001" in versions


class TestDeploymentScripts:
    """Test DeploymentScripts"""
    
    def test_pre_deploy_checks(self, tmp_path):
        """Test pre-deployment checks"""
        scripts = DeploymentScripts(tmp_path)
        result = scripts.pre_deploy_checks()
        assert isinstance(result, DeploymentResult)
        assert "checks" in result.details
    
    def test_get_status(self, tmp_path):
        """Test deployment status"""
        scripts = DeploymentScripts(tmp_path)
        result = scripts.get_status()
        assert isinstance(result, DeploymentResult)


class TestConfigValidator:
    """Test ConfigValidator"""
    
    def test_missing_config(self):
        """Test missing config file"""
        validator = ConfigValidator("nonexistent.yaml")
        result = validator.validate()
        assert result["valid"] is False
        assert len(result["errors"]) > 0
    
    def test_valid_config(self, tmp_path):
        """Test valid configuration"""
        config_content = """
engine:
  name: "Test"
  version: "1.0.0"
  environment: "production"
database:
  url: "sqlite:///test.db"
logging:
  level: "INFO"
security:
  secret_key: "test-secret-key"
  encryption_key: "test-encryption-key"
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        
        validator = ConfigValidator(str(config_file))
        result = validator.validate()
        assert result["valid"] is True


class TestRollbackManager:
    """Test RollbackManager"""
    
    def test_create_rollback_plan(self, tmp_path):
        """Test rollback plan creation"""
        manager = RollbackManager(tmp_path)
        plan = manager.create_rollback_plan("v1.0.0")
        
        assert plan.version == "v1.0.0"
        assert len(plan.steps) > 0
        assert plan.rollback_type == "full"
    
    def test_get_rollback_history(self, tmp_path):
        """Test rollback history"""
        manager = RollbackManager(tmp_path)
        history = manager.get_rollback_history()
        assert isinstance(history, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
