#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Optimization Tests
Tests for Autonomous Optimization Engine.
"""

import os
import sys
import json
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture(scope="function")
def temp_dir():
    """Create temporary directory"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture(scope="function")
def db_manager(temp_dir):
    """Create database manager"""
    from shared.database import DatabaseManager
    db_path = temp_dir / "optimization.db"
    return DatabaseManager(db_path)


class TestPolicyEngine:
    """Test policy engine"""
    
    def test_default_policies_loaded(self, db_manager):
        from optimization.engines.policy_engine import PolicyEngine
        engine = PolicyEngine(db_manager)
        policies = engine.get_policies()
        assert len(policies) > 0
    
    def test_policy_allowed(self, db_manager):
        from optimization.engines.policy_engine import PolicyEngine
        from optimization.core.optimization_core import OptimizationContext, OptimizationMode
        
        engine = PolicyEngine(db_manager)
        context = OptimizationContext(
            optimization_id="opt-test",
            mode=OptimizationMode.RECOMMENDATION,
            category="pricing",
            target_metric="revenue",
            current_value=1000.0,
            expected_value=1100.0,
            confidence=0.8,
            risk_score=0.2,
            status="pending"
        )
        
        data = {"price_change_percent": 10, "confidence": 0.8, "risk_score": 0.2, "marketplace_compliant": True, "expected_revenue_impact": 500}
        evaluation = engine.evaluate(context, data)
        assert evaluation.result.value == "allowed"
    
    def test_policy_denied(self, db_manager):
        from optimization.engines.policy_engine import PolicyEngine
        from optimization.core.optimization_core import OptimizationContext, OptimizationMode
        
        engine = PolicyEngine(db_manager)
        context = OptimizationContext(
            optimization_id="opt-test",
            mode=OptimizationMode.RECOMMENDATION,
            category="pricing",
            target_metric="revenue",
            current_value=1000.0,
            expected_value=1100.0,
            confidence=0.8,
            risk_score=0.2,
            status="pending"
        )
        
        data = {"price_change_percent": 100, "confidence": 0.8, "risk_score": 0.2}
        evaluation = engine.evaluate(context, data)
        assert evaluation.result.value == "denied"


class TestDecisionEngine:
    """Test decision engine"""
    
    def test_create_decision(self, db_manager):
        from optimization.engines.decision_engine import DecisionEngine
        from optimization.engines.confidence_engine import ConfidenceEngine
        from optimization.engines.risk_engine import RiskEngine
        from optimization.engines.simulation_engine import SimulationEngine
        from optimization.core.optimization_core import OptimizationContext, OptimizationMode
        
        dec_engine = DecisionEngine(db_manager, ConfidenceEngine(), RiskEngine(), SimulationEngine(db_manager))
        
        context = OptimizationContext(
            optimization_id="opt-test",
            mode=OptimizationMode.RECOMMENDATION,
            category="pricing",
            target_metric="revenue",
            current_value=1000.0,
            expected_value=1100.0,
            confidence=0.0,
            risk_score=0.0,
            status="pending"
        )
        
        optimizer_result = {"reason": "Test", "evidence": {}, "expected_impact": {}}
        simulation_result = {"expected_impact": {"revenue": 100.0}, "rollback_plan": {}, "related_metrics": []}
        
        decision = dec_engine.create_decision(context, optimizer_result, simulation_result)
        assert decision.decision_id is not None
        assert decision.confidence > 0
        assert decision.risk_score > 0
    
    def test_approve_decision(self, db_manager):
        from optimization.engines.decision_engine import DecisionEngine
        from optimization.engines.confidence_engine import ConfidenceEngine
        from optimization.engines.risk_engine import RiskEngine
        from optimization.engines.simulation_engine import SimulationEngine
        from optimization.core.optimization_core import OptimizationContext, OptimizationMode
        
        dec_engine = DecisionEngine(db_manager, ConfidenceEngine(), RiskEngine(), SimulationEngine(db_manager))
        
        context = OptimizationContext(
            optimization_id="opt-test",
            mode=OptimizationMode.RECOMMENDATION,
            category="pricing",
            target_metric="revenue",
            current_value=1000.0,
            expected_value=1100.0,
            confidence=0.0,
            risk_score=0.0,
            status="pending"
        )
        
        optimizer_result = {"reason": "Test", "evidence": {}, "expected_impact": {}}
        simulation_result = {"expected_impact": {"revenue": 100.0}, "rollback_plan": {}, "related_metrics": []}
        
        decision = dec_engine.create_decision(context, optimizer_result, simulation_result)
        approved = dec_engine.approve_decision(decision.decision_id, "admin")
        
        assert approved is not None
        assert approved.status.value == "approved"
        assert approved.decided_by == "admin"


class TestConfidenceEngine:
    """Test confidence engine"""
    
    def test_calculate_confidence(self):
        from optimization.engines.confidence_engine import ConfidenceEngine
        
        engine = ConfidenceEngine()
        
        optimizer_result = {
            "historical_accuracy": 0.8,
            "data_points": 100,
            "missing_data_percent": 0.05,
            "sample_size": 500,
            "simulation_variance": 0.1,
            "market_volatility": 0.2
        }
        
        confidence = engine.calculate(Mock(), optimizer_result)
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.6
    
    def test_low_confidence(self):
        from optimization.engines.confidence_engine import ConfidenceEngine
        
        engine = ConfidenceEngine()
        
        optimizer_result = {
            "historical_accuracy": 0.3,
            "data_points": 5,
            "missing_data_percent": 0.3,
            "sample_size": 10,
            "simulation_variance": 0.5,
            "market_volatility": 0.6
        }
        
        confidence = engine.calculate(Mock(), optimizer_result)
        assert confidence < 0.6


class TestRiskEngine:
    """Test risk engine"""
    
    def test_assess_risk(self):
        from optimization.engines.risk_engine import RiskEngine
        from optimization.core.optimization_core import OptimizationContext, OptimizationMode
        
        engine = RiskEngine()
        
        context = OptimizationContext(
            optimization_id="opt-test",
            mode=OptimizationMode.RECOMMENDATION,
            category="pricing",
            target_metric="revenue",
            current_value=1000.0,
            expected_value=1100.0,
            confidence=0.8,
            risk_score=0.0,
            status="pending"
        )
        
        optimizer_result = {
            "revenue_impact": 500,
            "max_revenue_impact": 10000,
            "complexity": 0.3,
            "dependencies": [],
            "marketplace_changes": 0,
            "max_marketplace_changes": 5,
            "customer_impact_score": 0.2,
            "compliance_issues": 0,
            "technical_complexity": 0.2,
            "rollback_complexity": 0.1
        }
        
        assessment = engine.assess(context, optimizer_result)
        assert 0.0 <= assessment.risk_score <= 1.0
        assert len(assessment.mitigation_steps) >= 0


class TestSimulationEngine:
    """Test simulation engine"""
    
    def test_run_simulation(self, db_manager):
        from optimization.engines.simulation_engine import SimulationEngine
        from optimization.core.optimization_core import OptimizationContext, OptimizationMode
        
        engine = SimulationEngine(db_manager)
        
        context = OptimizationContext(
            optimization_id="opt-test",
            mode=OptimizationMode.RECOMMENDATION,
            category="pricing",
            target_metric="revenue",
            current_value=1000.0,
            expected_value=1100.0,
            confidence=0.8,
            risk_score=0.2,
            status="pending"
        )
        
        optimizer_result = {
            "revenue_factor": 1.1,
            "traffic_factor": 1.05,
            "conversion_factor": 1.08,
            "refund_factor": 0.95,
            "current_revenue": 1000.0,
            "current_traffic": 10000.0,
            "current_conversion": 0.02,
            "current_refund_rate": 0.05
        }
        
        result = engine.run_simulation(context, optimizer_result)
        assert result.status.value == "completed"
        assert "revenue" in result.expected_impact
        assert len(result.rollback_plan["steps"]) > 0


class TestRuleEngine:
    """Test rule engine"""
    
    def test_default_rules_loaded(self, db_manager):
        from optimization.engines.rule_engine import RuleEngine
        engine = RuleEngine(db_manager)
        rules = engine.get_rules()
        assert len(rules) > 0
    
    def test_evaluate_rules(self, db_manager):
        from optimization.engines.rule_engine import RuleEngine
        
        engine = RuleEngine(db_manager)
        metrics = {"conversion_rate": 0.01, "refund_rate": 0.06}
        
        triggered = engine.evaluate_rules(metrics)
        assert len(triggered) > 0


class TestRecommendationEngine:
    """Test recommendation engine"""
    
    def test_generate_recommendation(self, db_manager):
        from optimization.engines.recommendation_engine import RecommendationEngine
        from optimization.core.optimization_core import OptimizationContext, OptimizationMode
        
        engine = RecommendationEngine(db_manager)
        
        context = OptimizationContext(
            optimization_id="opt-test",
            mode=OptimizationMode.RECOMMENDATION,
            category="pricing",
            target_metric="revenue",
            current_value=1000.0,
            expected_value=1100.0,
            confidence=0.8,
            risk_score=0.2,
            status="pending"
        )
        
        optimizer_result = {
            "title": "Price Optimization",
            "description": "Optimize pricing strategy",
            "evidence": {},
            "expected_impact": {"revenue": 100.0}
        }
        
        recommendation = engine.generate(context, optimizer_result, 0.8, 0.2)
        assert recommendation.recommendation_id is not None
        assert recommendation.confidence == 0.8


class TestExperimentEngine:
    """Test experiment engine"""
    
    def test_create_experiment(self, db_manager):
        from optimization.engines.experiment_engine import ExperimentEngine, ExperimentType
        from optimization.infrastructure.rollback_engine import RollbackEngine
        
        rollback = RollbackEngine(db_manager)
        engine = ExperimentEngine(db_manager, rollback)
        
        experiment = engine.create_experiment("opt-123", ExperimentType.A_B_TEST, {"variant_a": "control", "variant_b": "treatment"})
        assert experiment.experiment_id is not None
        assert experiment.experiment_type == ExperimentType.A_B_TEST
    
    def test_start_experiment(self, db_manager):
        from optimization.engines.experiment_engine import ExperimentEngine, ExperimentType
        from optimization.infrastructure.rollback_engine import RollbackEngine
        
        rollback = RollbackEngine(db_manager)
        engine = ExperimentEngine(db_manager, rollback)
        
        experiment = engine.create_experiment("opt-123", ExperimentType.CANARY, {"percentage": 10})
        result = engine.start_experiment(experiment.experiment_id)
        assert result is True


class TestApprovalWorkflow:
    """Test approval workflow"""
    
    def test_create_request(self, db_manager):
        from optimization.infrastructure.approval_workflow import ApprovalWorkflow
        
        workflow = ApprovalWorkflow(db_manager)
        request = workflow.create_request("opt-123", "dec-123", "system", "Test approval", {})
        
        assert request.request_id is not None
        assert request.status.value == "pending"
    
    def test_approve_request(self, db_manager):
        from optimization.infrastructure.approval_workflow import ApprovalWorkflow
        
        workflow = ApprovalWorkflow(db_manager)
        request = workflow.create_request("opt-123", "dec-123", "system", "Test approval", {})
        
        approved = workflow.approve(request.request_id, "admin")
        assert approved is not None
        assert approved.status.value == "approved"
        assert approved.approver == "admin"


class TestRollbackEngine:
    """Test rollback engine"""
    
    def test_record_states(self, db_manager):
        from optimization.infrastructure.rollback_engine import RollbackEngine
        
        engine = RollbackEngine(db_manager)
        rollback_id = engine.record_before_state("opt-123", {"price": 100})
        
        assert rollback_id is not None
        engine.record_after_state(rollback_id, {"price": 110})
        engine.set_rollback_plan(rollback_id, ["restore price"], ["verify price"])
    
    def test_execute_rollback(self, db_manager):
        from optimization.infrastructure.rollback_engine import RollbackEngine
        
        engine = RollbackEngine(db_manager)
        rollback_id = engine.record_before_state("opt-123", {"price": 100})
        engine.record_after_state(rollback_id, {"price": 110})
        engine.set_rollback_plan(rollback_id, ["restore price"], ["verify price"])
        
        result = engine.rollback("opt-123", "test rollback")
        assert result is True


class TestMetricsCollector:
    """Test metrics collector"""
    
    def test_record_metrics(self):
        from optimization.infrastructure.metrics_collector import MetricsCollector
        
        metrics = MetricsCollector()
        metrics.record_recommendation_generated()
        metrics.record_recommendation_approved()
        metrics.record_confidence(0.8)
        metrics.record_revenue_improvement(1000.0)
        
        data = metrics.get_metrics()
        assert data["recommendations_generated"] == 1
        assert data["recommendations_approved"] == 1
        assert data["average_confidence"] == 0.8
        assert data["revenue_improvement"] == 1000.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
