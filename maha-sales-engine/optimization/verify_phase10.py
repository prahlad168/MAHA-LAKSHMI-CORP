#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Verify Phase 10 Outputs
Verifies all Phase 10 deliverables.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def verify_folder_tree():
    """Verify folder tree"""
    base = Path(__file__).parent
    
    required_dirs = [
        "core",
        "engines",
        "optimizers",
        "infrastructure",
        "api",
        "db",
        "tests",
        "docs"
    ]
    
    required_files = [
        "core/optimization_core.py",
        "engines/policy_engine.py",
        "engines/decision_engine.py",
        "engines/confidence_engine.py",
        "engines/risk_engine.py",
        "engines/simulation_engine.py",
        "engines/experiment_engine.py",
        "engines/learning_engine.py",
        "engines/recommendation_engine.py",
        "engines/rule_engine.py",
        "optimizers/pricing_engine.py",
        "optimizers/marketplace_optimizer.py",
        "optimizers/marketing_optimizer.py",
        "optimizers/seo_optimizer.py",
        "optimizers/product_optimizer.py",
        "optimizers/campaign_optimizer.py",
        "optimizers/customer_retention_engine.py",
        "optimizers/forecast_engine.py",
        "infrastructure/rollback_engine.py",
        "infrastructure/approval_workflow.py",
        "infrastructure/optimization_queue.py",
        "infrastructure/event_bus.py",
        "infrastructure/scheduler.py",
        "infrastructure/metrics_collector.py",
        "infrastructure/audit_engine.py",
        "infrastructure/health_monitor.py",
        "api/routes.py",
        "db/schema.sql",
        "db/optimization_db.py",
        "tests/test_optimization.py",
        "docs/AUTONOMOUS_OPTIMIZATION_ENGINE.md",
        "docs/DECISION_ENGINE.md",
        "docs/SIMULATION_ENGINE.md",
        "docs/POLICY_ENGINE.md",
        "docs/RISK_ENGINE.md",
        "docs/CONFIDENCE_ENGINE.md",
        "docs/ROLLBACK_ENGINE.md",
        "docs/EXPERIMENT_ENGINE.md"
    ]
    
    missing_dirs = [d for d in required_dirs if not (base / d).is_dir()]
    missing_files = [f for f in required_files if not (base / f).is_file()]
    
    print("=== Folder Tree Verification ===")
    print(f"Base directory: {base}")
    print(f"Required directories: {len(required_dirs)}")
    print(f"Missing directories: {len(missing_dirs)}")
    if missing_dirs:
        for d in missing_dirs:
            print(f"  - {d}")
    
    print(f"\nRequired files: {len(required_files)}")
    print(f"Missing files: {len(missing_files)}")
    if missing_files:
        for f in missing_files:
            print(f"  - {f}")
    
    return len(missing_dirs) == 0 and len(missing_files) == 0


def verify_database_schema():
    """Verify database schema"""
    schema_path = Path(__file__).parent / "db" / "schema.sql"
    
    required_tables = [
        "optimization_jobs",
        "optimization_rules",
        "optimization_results",
        "recommendations",
        "decision_history",
        "simulation_results",
        "confidence_scores",
        "risk_assessments",
        "rollback_history",
        "approval_requests",
        "policy_evaluations",
        "optimization_metrics"
    ]
    
    if not schema_path.exists():
        print("\n=== Database Schema Verification ===")
        print("FAIL: schema.sql not found")
        return False
    
    schema_text = schema_path.read_text()
    
    missing_tables = [t for t in required_tables if f"CREATE TABLE IF NOT EXISTS {t}" not in schema_text]
    
    print("\n=== Database Schema Verification ===")
    print(f"Required tables: {len(required_tables)}")
    print(f"Missing tables: {len(missing_tables)}")
    if missing_tables:
        for t in missing_tables:
            print(f"  - {t}")
    
    return len(missing_tables) == 0


def verify_api_routes():
    """Verify API routes"""
    routes_path = Path(__file__).parent / "api" / "routes.py"
    
    if not routes_path.exists():
        print("\n=== API Routes Verification ===")
        print("FAIL: routes.py not found")
        return False
    
    routes_text = routes_path.read_text()
    
    required_endpoints = [
        "/health",
        "/api/v1/optimizations",
        "/api/v1/optimizations/{optimization_id}/recommend",
        "/api/v1/optimizations/{optimization_id}/simulate",
        "/api/v1/optimizations/{optimization_id}/approve",
        "/api/v1/optimizations/{optimization_id}/reject",
        "/api/v1/optimizations/{optimization_id}/execute",
        "/api/v1/optimizations/{optimization_id}/rollback",
        "/api/v1/recommendations",
        "/api/v1/approvals/pending",
        "/api/v1/metrics",
        "/api/v1/policies"
    ]
    
    missing_endpoints = [e for e in required_endpoints if e not in routes_text]
    
    print("\n=== API Routes Verification ===")
    print(f"Required endpoints: {len(required_endpoints)}")
    print(f"Missing endpoints: {len(missing_endpoints)}")
    if missing_endpoints:
        for e in missing_endpoints:
            print(f"  - {e}")
    
    return len(missing_endpoints) == 0


def verify_tests():
    """Verify tests exist and can be imported"""
    test_path = Path(__file__).parent / "tests" / "test_optimization.py"
    
    print("\n=== Tests Verification ===")
    if not test_path.exists():
        print("FAIL: test_optimization.py not found")
        return False
    
    print("Test file exists: test_optimization.py")
    
    # Try importing
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        import importlib.util
        spec = importlib.util.spec_from_file_location("test_optimization", test_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print("Test module imports successfully")
        return True
    except Exception as e:
        print(f"FAIL: Test import error: {e}")
        return False


def verify_documentation():
    """Verify documentation files"""
    docs_path = Path(__file__).parent / "docs"
    
    required_docs = [
        "AUTONOMOUS_OPTIMIZATION_ENGINE.md",
        "DECISION_ENGINE.md",
        "SIMULATION_ENGINE.md",
        "POLICY_ENGINE.md",
        "RISK_ENGINE.md",
        "CONFIDENCE_ENGINE.md",
        "ROLLBACK_ENGINE.md",
        "EXPERIMENT_ENGINE.md"
    ]
    
    missing_docs = [d for d in required_docs if not (docs_path / d).exists()]
    
    print("\n=== Documentation Verification ===")
    print(f"Required docs: {len(required_docs)}")
    print(f"Missing docs: {len(missing_docs)}")
    if missing_docs:
        for d in missing_docs:
            print(f"  - {d}")
    
    return len(missing_docs) == 0


def main():
    print("=" * 60)
    print("MAHA SALES ENGINE V1 - Phase 10 Verification")
    print("=" * 60)
    
    results = {
        "Folder Tree": verify_folder_tree(),
        "Database Schema": verify_database_schema(),
        "API Routes": verify_api_routes(),
        "Tests": verify_tests(),
        "Documentation": verify_documentation()
    }
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"{name}: {status}")
    
    all_passed = all(results.values())
    print("\n" + "=" * 60)
    if all_passed:
        print("ALL VERIFICATIONS PASSED")
    else:
        print("SOME VERIFICATIONS FAILED")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
