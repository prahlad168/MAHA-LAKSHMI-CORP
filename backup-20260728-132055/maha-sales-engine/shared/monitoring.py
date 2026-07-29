#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Metrics & Monitoring
Prometheus metrics and application monitoring.
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import defaultdict
from functools import wraps

sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger("maha-sales-engine.metrics")


@dataclass
class MetricValue:
    name: str
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class MetricsCollector:
    """Collect and store application metrics"""
    
    def __init__(self):
        self._metrics: Dict[str, List[MetricValue]] = defaultdict(list)
        self._counters: Dict[str, float] = defaultdict(float)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, List[float]] = defaultdict(list)
    
    def increment(self, name: str, value: float = 1.0, labels: Dict[str, str] = None):
        """Increment counter metric"""
        key = self._make_key(name, labels)
        self._counters[key] += value
        self._record_metric(name, value, labels)
    
    def gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """Set gauge metric"""
        key = self._make_key(name, labels)
        self._gauges[key] = value
        self._record_metric(name, value, labels)
    
    def histogram(self, name: str, value: float, labels: Dict[str, str] = None):
        """Record histogram metric"""
        key = self._make_key(name, labels)
        self._histograms[key].append(value)
        
        # Keep only last 1000 values
        if len(self._histograms[key]) > 1000:
            self._histograms[key] = self._histograms[key][-1000:]
        
        self._record_metric(name, value, labels)
    
    def _make_key(self, name: str, labels: Dict[str, str] = None) -> str:
        """Make metric key"""
        if labels:
            label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
            return f"{name}[{label_str}]"
        return name
    
    def _record_metric(self, name: str, value: float, labels: Dict[str, str] = None):
        """Record metric value"""
        metric = MetricValue(
            name=name,
            value=value,
            labels=labels or {}
        )
        self._metrics[name].append(metric)
        
        # Keep only last 1000 values
        if len(self._metrics[name]) > 1000:
            self._metrics[name] = self._metrics[name][-1000:]
    
    def get_counter(self, name: str, labels: Dict[str, str] = None) -> float:
        """Get counter value"""
        key = self._make_key(name, labels)
        return self._counters.get(key, 0.0)
    
    def get_gauge(self, name: str, labels: Dict[str, str] = None) -> float:
        """Get gauge value"""
        key = self._make_key(name, labels)
        return self._gauges.get(key, 0.0)
    
    def get_histogram_stats(self, name: str, labels: Dict[str, str] = None) -> Dict[str, float]:
        """Get histogram statistics"""
        key = self._make_key(name, labels)
        values = self._histograms.get(key, [])
        
        if not values:
            return {"count": 0, "min": 0, "max": 0, "avg": 0, "p95": 0, "p99": 0}
        
        sorted_values = sorted(values)
        count = len(sorted_values)
        
        return {
            "count": count,
            "min": sorted_values[0],
            "max": sorted_values[-1],
            "avg": sum(sorted_values) / count,
            "p95": sorted_values[int(count * 0.95)],
            "p99": sorted_values[int(count * 0.99)]
        }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics"""
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histograms": {
                name: self.get_histogram_stats(name)
                for name in self._histograms.keys()
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def reset(self):
        """Reset all metrics"""
        self._metrics.clear()
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()


class PrometheusExporter:
    """Export metrics in Prometheus format"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
    
    def export(self) -> str:
        """Export metrics in Prometheus text format"""
        lines = []
        
        # Export counters
        for key, value in self.collector._counters.items():
            name, labels = self._parse_key(key)
            label_str = self._format_labels(labels)
            lines.append(f"# TYPE {name} counter")
            lines.append(f"{name}{label_str} {value}")
        
        # Export gauges
        for key, value in self.collector._gauges.items():
            name, labels = self._parse_key(key)
            label_str = self._format_labels(labels)
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name}{label_str} {value}")
        
        # Export histograms
        for key, values in self.collector._histograms.items():
            name, labels = self._parse_key(key)
            stats = self.collector.get_histogram_stats(name, labels)
            label_str = self._format_labels(labels)
            
            lines.append(f"# TYPE {name} histogram")
            lines.append(f"{name}_count{label_str} {stats['count']}")
            lines.append(f"{name}_sum{label_str} {stats['count'] * stats['avg']}")
            lines.append(f"{name}_bucket{{le=\"0.1\"}}{label_str} {len([v for v in values if v <= 0.1])}")
            lines.append(f"{name}_bucket{{le=\"0.5\"}}{label_str} {len([v for v in values if v <= 0.5])}")
            lines.append(f"{name}_bucket{{le=\"1.0\"}}{label_str} {len([v for v in values if v <= 1.0])}")
            lines.append(f"{name}_bucket{{le=\"+Inf\"}}{label_str} {stats['count']}")
        
        return "\n".join(lines) + "\n"
    
    def _parse_key(self, key: str) -> tuple:
        """Parse metric key into name and labels"""
        if "[" in key:
            name, rest = key.split("[", 1)
            labels_str = rest.rstrip("]")
            labels = {}
            for part in labels_str.split(","):
                k, v = part.split("=", 1)
                labels[k] = v
            return name, labels
        return key, {}
    
    def _format_labels(self, labels: Dict[str, str]) -> str:
        """Format labels for Prometheus"""
        if not labels:
            return ""
        label_str = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        return f"{{{label_str}}}"


# Global metrics collector
metrics = MetricsCollector()
prometheus = PrometheusExporter(metrics)


def get_metrics() -> MetricsCollector:
    """Get global metrics collector"""
    return metrics


def get_prometheus_exporter() -> PrometheusExporter:
    """Get Prometheus exporter"""
    return prometheus


def measure_time(metric_name: str, labels: Dict[str, str] = None):
    """Decorator to measure execution time"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start
                metrics.histogram(metric_name, elapsed, labels)
                return result
            except Exception as e:
                elapsed = time.time() - start
                metrics.histogram(f"{metric_name}_error", elapsed, labels)
                raise
        return wrapper
    return decorator


def count_calls(metric_name: str, labels: Dict[str, str] = None):
    """Decorator to count function calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            metrics.increment(metric_name, 1.0, labels)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def main():
    """Test metrics system"""
    print("Metrics system loaded")
    
    metrics.increment("test_counter", 1.0, {"endpoint": "/test"})
    metrics.gauge("test_gauge", 42.0)
    metrics.histogram("test_latency", 0.123)
    
    print(f"Metrics: {metrics.get_all_metrics()}")


if __name__ == "__main__":
    main()
