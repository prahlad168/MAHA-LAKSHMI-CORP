#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Verify Phase 11 Outputs
Verifies all Phase 11 deliverables.
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
        "infrastructure",
        "api",
        "db",
        "tests",
        "docs"
    ]
    
    required_files = [
        "core/knowledge_core.py",
        "engines/learning_engine.py",
        "engines/memory_engine.py",
        "engines/pattern_recognition.py",
        "engines/knowledge_graph.py",
        "engines/semantic_search.py",
        "engines/embedding_service.py",
        "engines/document_indexer.py",
        "engines/knowledge_validator.py",
        "engines/knowledge_repository.py",
        "engines/decision_memory.py",
        "engines/experiment_memory.py",
        "infrastructure/knowledge_versioning.py",
        "infrastructure/knowledge_event_bus.py",
        "infrastructure/knowledge_metrics.py",
        "infrastructure/knowledge_audit.py",
        "infrastructure/health_monitor.py",
        "api/routes.py",
        "db/schema.sql",
        "db/knowledge_db.py",
        "tests/test_knowledge.py",
        "docs/KNOWLEDGE_PLATFORM.md",
        "docs/LEARNING_ENGINE.md",
        "docs/MEMORY_ENGINE.md",
        "docs/KNOWLEDGE_GRAPH.md",
        "docs/SEMANTIC_SEARCH.md",
        "docs/DECISION_MEMORY.md"
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
        "knowledge_items",
        "knowledge_versions",
        "knowledge_sources",
        "decision_memory",
        "experiment_memory",
        "pattern_library",
        "knowledge_graph_nodes",
        "knowledge_graph_edges",
        "learning_events",
        "semantic_embeddings"
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
        "/api/v1/knowledge",
        "/api/v1/knowledge/search",
        "/api/v1/knowledge/semantic-search",
        "/api/v1/decisions",
        "/api/v1/experiments",
        "/api/v1/patterns",
        "/api/v1/insights",
        "/api/v1/knowledge-graph",
        "/api/v1/metrics",
        "/api/v1/knowledge/{knowledge_id}/versions",
        "/api/v1/knowledge/record-learning",
        "/api/v1/memory/stats",
        "/api/v1/search/stats"
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
    test_path = Path(__file__).parent / "tests" / "test_knowledge.py"
    
    print("\n=== Tests Verification ===")
    if not test_path.exists():
        print("FAIL: test_knowledge.py not found")
        return False
    
    print("Test file exists: test_knowledge.py")
    
    # Try importing
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        import importlib.util
        spec = importlib.util.spec_from_file_location("test_knowledge", test_path)
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
        "KNOWLEDGE_PLATFORM.md",
        "LEARNING_ENGINE.md",
        "MEMORY_ENGINE.md",
        "KNOWLEDGE_GRAPH.md",
        "SEMANTIC_SEARCH.md",
        "DECISION_MEMORY.md"
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
    print("MAHA SALES ENGINE V1 - Phase 11 Verification")
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
