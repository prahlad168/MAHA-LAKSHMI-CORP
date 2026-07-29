#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Test Runner
Run all tests with coverage reporting.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_tests():
    """Run all tests"""
    print("=" * 60)
    print("MAHA SALES ENGINE V1 - Test Suite")
    print("=" * 60)
    
    test_dir = Path(__file__).parent
    test_files = list(test_dir.glob("test_*.py"))
    
    print(f"Found {len(test_files)} test files")
    
    # Run tests with coverage
    cmd = [
        "pytest",
        str(test_dir),
        "-v",
        "--tb=short",
        "--cov=.",
        "--cov-report=term-missing",
        "--cov-report=html",
        "--junitxml=test-results.xml"
    ]
    
    result = subprocess.run(cmd, cwd=test_dir.parent)
    
    print("\n" + "=" * 60)
    if result.returncode == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
    print("=" * 60)
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(run_tests())
