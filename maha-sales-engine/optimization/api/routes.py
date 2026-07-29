#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Optimization API Routes
REST API for Autonomous Optimization Engine.
"""

import os
import sys
import json
import time
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field

logger = logging.getLogger("maha-sales-engine.optimization.api")


# Pydantic models
class OptimizationRequest(BaseModel):
    category: str
    target_metric: str
    current_value: float
    expected_value: float
    mode: str = "recommendation"
    data: Dict[str, Any] = {}


class ApprovalRequest(BaseModel):
    request_id: str
    approved: bool
    approver: str
    reason: Optional[str] = None


class RollbackRequest(BaseModel):
    optimization_id: str
    reason: str


# Create FastAPI app
app = FastAPI(
    title="MAHA Sales Engine V1 - Optimization API",
    description="Autonomous Optimization Engine API",
    version="1.0.0"
)


# Dependency injection
def get_optimization_core():
    # In production, this would be injected from the app container
    from optimization.core.optimization_core import OptimizationCore
    from optimization.engines.policy_engine import PolicyEngine
    from optimization.infrastructure.approval_workflow import ApprovalWorkflow
    from optimization.infrastructure.rollback_engine import RollbackEngine
    from optimization.db.optimization_db import OptimizationDatabaseManager
    from shared.database import DatabaseManager
    
    db = DatabaseManager("data/optimization.db")
    policy_engine = PolicyEngine(db)
    approval_workflow = ApprovalWorkflow(db)
    rollback_engine = RollbackEngine(db)
    opt_db = OptimizationDatabaseManager(db)
    
    return OptimizationCore(db, policy_engine, approval_workflow, rollback_engine)


def get_policy_engine():
    from optimization.engines.policy_engine import PolicyEngine
    from shared.database import DatabaseManager
    db = DatabaseManager("data/optimization.db")
    return PolicyEngine(db)


def get_decision_engine():
    from optimization.engines.decision_engine import DecisionEngine
    from optimization.engines.confidence_engine import ConfidenceEngine
    from optimization.engines.risk_engine import RiskEngine
    from optimization.engines.simulation_engine import SimulationEngine
    from shared.database import DatabaseManager
    db = DatabaseManager("data/optimization.db")
    return DecisionEngine(db, ConfidenceEngine(), RiskEngine(), SimulationEngine(db))


def get_recommendation_engine():
    from optimization.engines.recommendation_engine import RecommendationEngine
    from shared.database import DatabaseManager
    db = DatabaseManager("data/optimization.db")
    return RecommendationEngine(db)


def get_simulation_engine():
    from optimization.engines.simulation_engine import SimulationEngine
    from shared.database import DatabaseManager
    db = DatabaseManager("data/optimization.db")
    return SimulationEngine(db)


def get_approval_workflow():
    from optimization.infrastructure.approval_workflow import ApprovalWorkflow
    from shared.database import DatabaseManager
    db = DatabaseManager("data/optimization.db")
    return ApprovalWorkflow(db)


def get_rollback_engine():
    from optimization.infrastructure.rollback_engine import RollbackEngine
    from shared.database import DatabaseManager
    db = DatabaseManager("data/optimization.db")
    return RollbackEngine(db)


def get_metrics_collector():
    from optimization.infrastructure.metrics_collector import MetricsCollector
    return MetricsCollector()


# API Endpoints

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "optimization", "version": "1.0.0"}


@app.post("/api/v1/optimizations")
async def create_optimization(request: OptimizationRequest, core = Depends(get_optimization_core)):
    """Create optimization request"""
    from optimization.core.optimization_core import OptimizationMode
    
    mode = OptimizationMode(request.mode)
    context = core.create_optimization(
        category=request.category,
        target_metric=request.target_metric,
        current_value=request.current_value,
        expected_value=request.expected_value,
        mode=mode
    )
    
    return {
        "optimization_id": context.optimization_id,
        "mode": context.mode.value,
        "status": context.status.value,
        "created_at": context.created_at
    }


@app.get("/api/v1/optimizations")
async def list_optimizations(status: Optional[str] = None, core = Depends(get_optimization_core)):
    """List optimizations"""
    from optimization.core.optimization_core import OptimizationStatus
    
    status_filter = OptimizationStatus(status) if status else None
    optimizations = core.list_optimizations(status=status_filter)
    
    return {
        "optimizations": [
            {
                "optimization_id": o.optimization_id,
                "category": o.category,
                "target_metric": o.target_metric,
                "status": o.status.value,
                "mode": o.mode.value,
                "created_at": o.created_at
            }
            for o in optimizations
        ]
    }


@app.post("/api/v1/optimizations/{optimization_id}/recommend")
async def generate_recommendation(optimization_id: str, core = Depends(get_optimization_core), rec_engine = Depends(get_recommendation_engine)):
    """Generate recommendation for optimization"""
    context = core.get_optimization(optimization_id)
    if not context:
        raise HTTPException(status_code=404, detail="Optimization not found")
    
    # Mock optimizer result
    optimizer_result = {
        "title": "Optimization Recommendation",
        "description": "Optimization opportunity identified",
        "evidence": {"metric_trend": "declining", "historical_accuracy": 0.8},
        "expected_impact": {"revenue": 1000.0, "conversion": 0.02},
        "reason": "Performance below target"
    }
    
    # Calculate confidence and risk
    confidence = 0.75
    risk_score = 0.3
    
    # Generate recommendation
    recommendation = rec_engine.generate(context, optimizer_result, confidence, risk_score)
    
    return {
        "recommendation_id": recommendation.recommendation_id,
        "optimization_id": recommendation.optimization_id,
        "title": recommendation.title,
        "description": recommendation.description,
        "confidence": recommendation.confidence,
        "risk_score": recommendation.risk_score,
        "expected_impact": recommendation.expected_impact,
        "mode": recommendation.mode
    }


@app.post("/api/v1/optimizations/{optimization_id}/simulate")
async def run_simulation(optimization_id: str, core = Depends(get_optimization_core), sim_engine = Depends(get_simulation_engine)):
    """Run simulation for optimization"""
    context = core.get_optimization(optimization_id)
    if not context:
        raise HTTPException(status_code=404, detail="Optimization not found")
    
    optimizer_result = {"revenue_factor": 1.1, "traffic_factor": 1.05, "conversion_factor": 1.08}
    result = sim_engine.run_simulation(context, optimizer_result)
    
    return {
        "simulation_id": result.simulation_id,
        "optimization_id": result.optimization_id,
        "status": result.status.value,
        "expected_impact": result.expected_impact,
        "confidence_interval": result.confidence_interval,
        "rollback_plan": result.rollback_plan,
        "related_metrics": result.related_metrics
    }


@app.post("/api/v1/optimizations/{optimization_id}/approve")
async def approve_optimization(optimization_id: str, request: ApprovalRequest, core = Depends(get_optimization_core), dec_engine = Depends(get_decision_engine), appr_workflow = Depends(get_approval_workflow)):
    """Approve optimization"""
    context = core.get_optimization(optimization_id)
    if not context:
        raise HTTPException(status_code=404, detail="Optimization not found")
    
    # Get decision
    decisions = dec_engine._decisions.values()
    decision = next((d for d in decisions if d.optimization_id == optimization_id and d.status.value == "pending"), None)
    
    if not decision:
        raise HTTPException(status_code=404, detail="Pending decision not found")
    
    # Approve decision
    dec_engine.approve_decision(decision.decision_id, request.approver)
    
    # Update approval request
    appr_workflow.approve(request.request_id, request.approver)
    
    return {
        "decision_id": decision.decision_id,
        "status": "approved",
        "approved_by": request.approver
    }


@app.post("/api/v1/optimizations/{optimization_id}/reject")
async def reject_optimization(optimization_id: str, request: ApprovalRequest, core = Depends(get_optimization_core), dec_engine = Depends(get_decision_engine), appr_workflow = Depends(get_approval_workflow)):
    """Reject optimization"""
    context = core.get_optimization(optimization_id)
    if not context:
        raise HTTPException(status_code=404, detail="Optimization not found")
    
    decisions = dec_engine._decisions.values()
    decision = next((d for d in decisions if d.optimization_id == optimization_id and d.status.value == "pending"), None)
    
    if not decision:
        raise HTTPException(status_code=404, detail="Pending decision not found")
    
    dec_engine.reject_decision(decision.decision_id, request.approver, request.reason or "Rejected")
    appr_workflow.reject(request.request_id, request.approver, request.reason or "Rejected")
    
    return {
        "decision_id": decision.decision_id,
        "status": "rejected",
        "rejected_by": request.approver
    }


@app.post("/api/v1/optimizations/{optimization_id}/execute")
async def execute_optimization(optimization_id: str, core = Depends(get_optimization_core), policy = Depends(get_policy_engine), rollback = Depends(get_rollback_engine), audit = Depends(get_audit_engine)):
    """Execute optimization"""
    context = core.get_optimization(optimization_id)
    if not context:
        raise HTTPException(status_code=404, detail="Optimization not found")
    
    # Validate policy
    policy_result = policy.evaluate(context, {"confidence": context.confidence, "risk_score": context.risk_score})
    if policy_result.result.value == "denied":
        raise HTTPException(status_code=403, detail=f"Policy violation: {policy_result.reason}")
    
    # Record before state
    rollback_id = rollback.record_before_state(optimization_id, {"status": "before"})
    
    # Execute optimization
    context.status = "executing"
    audit.log(optimization_id, "execute", "system", {"rollback_id": rollback_id})
    
    return {
        "optimization_id": optimization_id,
        "status": "executing",
        "rollback_id": rollback_id
    }


@app.post("/api/v1/optimizations/{optimization_id}/rollback")
async def rollback_optimization(optimization_id: str, request: RollbackRequest, rollback = Depends(get_rollback_engine), audit = Depends(get_audit_engine)):
    """Rollback optimization"""
    success = rollback.rollback(optimization_id, request.reason)
    if not success:
        raise HTTPException(status_code=404, detail="Rollback failed")
    
    audit.log(optimization_id, "rollback", "system", {"reason": request.reason})
    
    return {
        "optimization_id": optimization_id,
        "status": "rolled_back",
        "reason": request.reason
    }


@app.get("/api/v1/recommendations")
async def list_recommendations(category: Optional[str] = None, rec_engine = Depends(get_recommendation_engine)):
    """List recommendations"""
    recommendations = rec_engine.list_recommendations(category=category)
    return {"recommendations": recommendations}


@app.get("/api/v1/approvals/pending")
async def list_pending_approvals(appr_workflow = Depends(get_approval_workflow)):
    """List pending approval requests"""
    requests = appr_workflow.get_pending_requests()
    return {
        "pending_approvals": [
            {
                "request_id": r.request_id,
                "optimization_id": r.optimization_id,
                "requester": r.requester,
                "reason": r.reason,
                "expires_at": r.expires_at
            }
            for r in requests
        ]
    }


@app.get("/api/v1/metrics")
async def get_metrics(metrics = Depends(get_metrics_collector)):
    """Get optimization metrics"""
    return metrics.get_metrics()


@app.get("/api/v1/policies")
async def list_policies(policy = Depends(get_policy_engine)):
    """List policies"""
    policies = policy.get_policies()
    return {
        "policies": [
            {
                "policy_id": p.policy_id,
                "name": p.name,
                "type": p.policy_type.value,
                "description": p.description,
                "active": p.active
            }
            for p in policies
        ]
    }


def get_audit_engine():
    from optimization.infrastructure.audit_engine import AuditEngine
    from shared.database import DatabaseManager
    db = DatabaseManager("data/optimization.db")
    return AuditEngine(db)
