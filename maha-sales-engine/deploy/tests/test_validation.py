#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Production Validation Tests

Tests for production deployment validation.
"""

import sys
import os
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from deploy.validation.validator import ProductionValidator, ValidationResult
from deploy.benchmark.performance import PerformanceBenchmark, BenchmarkResult
from deploy.monitoring.uptime import UptimeMonitor, UptimeRecord
from deploy.monitoring.errors import ErrorAggregator
from deploy.scripts.deploy import DeploymentScripts, DeploymentResult
from deploy.scripts.validate_config import ConfigValidator
from deploy.rollback import RollbackManager
from deploy.migrations.runner import MigrationRunner, Migration


class TestProductionValidator:
    """Test ProductionValidator"""
    
    def test_validate_environment(self, monkeypatch):
        """Test environment validation"""
        validator = ProductionValidator()
        monkeypatch.setenv("MAHA_ENV", "production")
        result = validator._check_environment()
        assert result.passed is True
        assert "environment" in result.check_name
    
    def test_validate_docker(self):
        """Test docker validation"""
        validator = ProductionValidator()
        result = validator._check_docker()
        assert isinstance(result, ValidationResult)
    
    def test_validate_configuration(self, tmp_path):
        """Test configuration validation"""
        validator = ProductionValidator()
        
        with patch('deploy.validation.validator.Path') as mock_path:
            mock_path.return_value.exists.return_value = False
            result = validator._check_configuration()
            assert result.passed is False
    
    def test_validate_disk_space(self):
        """Test disk space validation"""
        validator = ProductionValidator()
        result = validator._check_disk_space()
        assert isinstance(result, ValidationResult)
    
    def test_validate_ports(self):
        """Test port validation"""
        validator = ProductionValidator()
        result = validator._check_ports()
        assert isinstance(result, ValidationResult)
    
    def test_run_all_checks(self, monkeypatch):
        """Test running all checks"""
        validator = ProductionValidator()
        monkeypatch.setenv("MAHA_ENV", "production")
        
        with patch('deploy.validation.validator.DatabaseManager') as mock_db:
            mock_db.return_value.execute.return_value = [{"1": 1}]
            mock_db.return_value.close.return_value = None
            
            with patch('deploy.validation.validator.get_engine') as mock_engine:
                mock_engine.return_value.get_health.return_value = {"status": "running"}
                result = validator.run_all_checks()
                assert "valid" in result
                assert "results" in result
    
    def test_generate_report(self, monkeypatch):
        """Test report generation"""
        validator = ProductionValidator()
        monkeypatch.setenv("MAHA_ENV", "production")
        
        with patch('deploy.validation.validator.DatabaseManager') as mock_db:
            mock_db.return_value.execute.return_value = [{"1": 1}]
            mock_db.return_value.close.return_value = None
            
            with patch('deploy.validation.validator.get_engine') as mock_engine:
                mock_engine.return_value.get_health.return_value = {"status": "running"}
                validator.run_all_checks()
                report = validator.generate_report()
                assert "Production Validation" in report


class TestPerformanceBenchmark:
    """Test PerformanceBenchmark"""
    
    def test_benchmark_database_queries(self, tmp_path):
        """Test database query benchmark"""
        benchmark = PerformanceBenchmark()
        result = benchmark._benchmark_database_queries(iterations=10)
        assert isinstance(result, BenchmarkResult)
        assert result.test_name == "database_queries"
        assert result.iterations == 10
    
    def test_benchmark_health_checks(self):
        """Test health check benchmark"""
        benchmark = PerformanceBenchmark()
        with patch('deploy.benchmark.performance.get_engine') as mock_engine:
            mock_engine.return_value.get_health.return_value = {"status": "running"}
            result = benchmark._benchmark_health_checks(iterations=10)
            assert isinstance(result, BenchmarkResult)
            assert result.test_name == "health_checks"
    
    def test_benchmark_event_bus(self):
        """Test event bus benchmark"""
        benchmark = PerformanceBenchmark()
        result = benchmark._benchmark_event_bus(iterations=10)
        assert isinstance(result, BenchmarkResult)
        assert result.test_name == "event_bus"
    
    def test_generate_summary(self):
        """Test summary generation"""
        benchmark = PerformanceBenchmark()
        result = benchmark._create_result("test", 10, [0.1, 0.2, 0.3])
        summary = benchmark._generate_summary()
        assert isinstance(summary, dict)
    
    def test_run_benchmarks(self):
        """Test running all benchmarks"""
        benchmark = PerformanceBenchmark()
        with patch('deploy.benchmark.performance.get_engine') as mock_engine:
            mock_engine.return_value.get_health.return_value = {"status": "running"}
            results = benchmark.run_benchmarks()
            assert "benchmarks" in results
            assert "summary" in results


class TestUptimeMonitor:
    """Test UptimeMonitor"""
    
    def test_check_uptime(self):
        """Test uptime check"""
        monitor = UptimeMonitor()
        with patch('deploy.monitoring.uptime.get_engine') as mock_engine:
            mock_engine.return_value.get_health.return_value = {"status": "running"}
            record = monitor.check_uptime()
            assert isinstance(record, UptimeRecord)
            assert record.status == "up"
    
    def test_get_uptime_stats(self):
        """Test uptime stats"""
        monitor = UptimeMonitor()
        stats = monitor.get_uptime_stats("1h")
        assert "period" in stats
        assert "uptime_percent" in stats
    
    def test_get_uptime_report(self):
        """Test uptime report"""
        monitor = UptimeMonitor()
        report = monitor.get_uptime_report()
        assert "timestamp" in report
        assert "uptime" in report
        assert "1h" in report["uptime"]
        assert "24h" in report["uptime"]


class TestErrorAggregator:
    """Test ErrorAggregator"""
    
    def test_analyze_logs(self, tmp_path):
        """Test log analysis"""
        aggregator = ErrorAggregator(log_dir=tmp_path)
        result = aggregator.analyze_logs(hours=1)
        assert "total_errors" in result
        assert "by_level" in result
        assert "by_module" in result
    
    def test_get_error_trend(self, tmp_path):
        """Test error trend"""
        aggregator = ErrorAggregator(log_dir=tmp_path)
        trend = aggregator.get_error_trend(hours=1)
        assert "period_hours" in trend
        assert "hourly_trend" in trend
    
    def test_generate_report(self, tmp_path):
        """Test report generation"""
        aggregator = ErrorAggregator(log_dir=tmp_path)
        report = aggregator.generate_report(hours=1)
        assert "Error Analysis Report" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
