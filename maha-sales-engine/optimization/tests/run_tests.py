#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Run Optimization Tests
Run all optimization tests.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_tests():
    """Run optimization tests"""
    print("=" * 60)
    print("MAHA SALES ENGINE V1 - Optimization Tests")
    print("=" * 60)
    
    test_dir = Path(__file__).parent
    result = subprocess.run(
        ["python3", "-m", "pytest", str(test_dir), "-v", "--tb=short"],
        cwd=test_dir.parent
    )
    
    print("\n" + "=" * 60)
    if result.returncode == 0:
        print("All optimization tests passed!")
    else:
        print("Some tests failed")
    print("=" * 60)
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(run_tests())
