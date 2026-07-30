#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Performance Benchmark

Performance benchmarking and load testing tools.
"""

import sys
import os
import json
import time
import logging
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.logging_utils import get_logger
from shared.core_engine import get_engine
from shared.database import DatabaseManager

logger = get_logger("deployment.benchmark")


@dataclass
class BenchmarkResult:
    """Benchmark result"""
    test_name: str
    iterations: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    ops_per_second: float
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_name": self.test_name,
            "iterations": self.iterations,
            "total_time": self.total_time,
            "avg_time": self.avg_time,
            "min_time": self.min_time,
            "max_time": self.max_time,
            "ops_per_second": self.ops_per_second,
            "timestamp": self.timestamp
        }


class PerformanceBenchmark:
    """Performance benchmarking tools"""
    
    def __init__(self):
        self.logger = get_logger("deployment.benchmark")
        self.results: List[BenchmarkResult] = []
    
    def run_benchmarks(self) -> Dict[str, Any]:
        """Run all benchmarks"""
        self.results = []
        
        benchmarks = [
            ("database_queries", self._benchmark_database_queries),
            ("health_checks", self._benchmark_health_checks),
            ("mission_operations", self._benchmark_mission_operations),
            ("metrics_aggregation", self._benchmark_metrics_aggregation),
            ("event_bus", self._benchmark_event_bus)
        ]
        
        results = {}
        for name, benchmark in benchmarks:
            try:
                result = benchmark()
                self.results.append(result)
                results[name] = result.to_dict()
            except Exception as e:
                self.logger.error(f"Benchmark failed: {name} - {e}")
                results[name] = {"error": str(e)}
        
        return {
            "benchmarks": results,
            "summary": self._generate_summary()
        }
    
    def _benchmark_database_queries(self, iterations: int = 100) -> BenchmarkResult:
        """Benchmark database queries"""
        db_path = os.environ.get("DATABASE_PATH", "data/benchmark.db")
        db = DatabaseManager(db_path)
        
        times = []
        for _ in range(iterations):
            start = time.time()
            db.execute("SELECT 1")
            times.append(time.time() - start)
        
        db.close()
        
        return self._create_result("database_queries", iterations, times)
    
    def _benchmark_health_checks(self, iterations: int = 50) -> BenchmarkResult:
        """Benchmark health checks"""
        engine = get_engine()
        
        times = []
        for _ in range(iterations):
            start = time.time()
            engine.get_health()
            times.append(time.time() - start)
        
        return self._create_result("health_checks", iterations, times)
    
    def _benchmark_mission_operations(self, iterations: int = 50) -> BenchmarkResult:
        """Benchmark mission control operations"""
        from mission_control.core.mission_controller import MissionController
        
        controller = MissionController()
        times = []
        
        for _ in range(iterations):
            start = time.time()
            controller.get_controller_metrics()
            times.append(time.time() - start)
        
        return self._create_result("mission_operations", iterations, times)
    
    def _benchmark_metrics_aggregation(self, iterations: int = 30) -> BenchmarkResult:
        """Benchmark metrics aggregation"""
        from mission_control.integrations.metrics import MetricsAggregator
        from shared.monitoring import MetricsCollector
        
        collector = MetricsCollector()
        aggregator = MetricsAggregator(None, collector)
        
        times = []
        for _ in range(iterations):
            start = time.time()
            aggregator.aggregate_all_metrics()
            times.append(time.time() - start)
        
        return self._create_result("metrics_aggregation", iterations, times)
    
    def _benchmark_event_bus(self, iterations: int = 100) -> BenchmarkResult:
        """Benchmark event bus"""
        from mission_control.integrations.event_bus import EventBus, Event
        
        bus = EventBus()
        
        def handler(event):
            pass
        
        bus.subscribe("test.benchmark", handler)
        
        times = []
        for _ in range(iterations):
            event = Event("test.benchmark", {"data": "test"})
            start = time.time()
            bus.publish(event)
            times.append(time.time() - start)
        
        return self._create_result("event_bus", iterations, times)
    
    def _create_result(self, name: str, iterations: int, times: List[float]) -> BenchmarkResult:
        """Create benchmark result from timing data"""
        total_time = sum(times)
        avg_time = total_time / len(times) if times else 0
        min_time = min(times) if times else 0
        max_time = max(times) if times else 0
        ops_per_second = iterations / total_time if total_time > 0 else 0
        
        return BenchmarkResult(
            test_name=name,
            iterations=iterations,
            total_time=total_time,
            avg_time=avg_time,
            min_time=min_time,
            max_time=max_time,
            ops_per_second=ops_per_second
        )
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate benchmark summary"""
        if not self.results:
            return {}
        
        total_ops = sum(r.iterations for r in self.results)
        total_time = sum(r.total_time for r in self.results)
        
        return {
            "total_tests": len(self.results),
            "total_operations": total_ops,
            "total_time": total_time,
            "overall_ops_per_second": total_ops / total_time if total_time > 0 else 0,
            "slowest_test": max(self.results, key=lambda r: r.avg_time).test_name,
            "fastest_test": min(self.results, key=lambda r: r.avg_time).test_name
        }
    
    def generate_report(self) -> str:
        """Generate benchmark report"""
        results = self.run_benchmarks()
        
        report = []
        report.append("=" * 60)
        report.append("MAHA SALES ENGINE V1 - Performance Benchmark")
        report.append("=" * 60)
        report.append(f"Timestamp: {datetime.now().isoformat()}")
        report.append("")
        
        for name, data in results["benchmarks"].items():
            if "error" in data:
                report.append(f"[ERROR] {name}: {data['error']}")
            else:
                report.append(f"[{name}]")
                report.append(f"  Iterations: {data['iterations']}")
                report.append(f"  Avg Time: {data['avg_time']*1000:.2f}ms")
                report.append(f"  Min Time: {data['min_time']*1000:.2f}ms")
                report.append(f"  Max Time: {data['max_time']*1000:.2f}ms")
                report.append(f"  Ops/sec: {data['ops_per_second']:.2f}")
                report.append("")
        
        report.append("Summary:")
        summary = results["summary"]
        report.append(f"  Total Tests: {summary.get('total_tests', 0)}")
        report.append(f"  Overall Ops/sec: {summary.get('overall_ops_per_second', 0):.2f}")
        report.append(f"  Slowest: {summary.get('slowest_test', 'N/A')}")
        report.append(f"  Fastest: {summary.get('fastest_test', 'N/A')}")
        report.append("=" * 60)
        
        return "\n".join(report)


def main():
    """CLI for performance benchmark"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Performance benchmark")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    benchmark = PerformanceBenchmark()
    
    if args.json:
        results = benchmark.run_benchmarks()
        print(json.dumps(results, indent=2, default=str))
    else:
        print(benchmark.generate_report())


if __name__ == "__main__":
    main()
