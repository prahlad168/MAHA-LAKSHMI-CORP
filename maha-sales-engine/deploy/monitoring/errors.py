#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Error Aggregator

Aggregates and analyzes production errors.
"""

import sys
import os
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.logging_utils import get_logger

logger = get_logger("deployment.errors")


@dataclass
class ErrorRecord:
    """Error record"""
    timestamp: str
    level: str
    message: str
    module: str
    function: str
    traceback: Optional[str] = None
    count: int = 1


class ErrorAggregator:
    """Aggregates and analyzes production errors"""
    
    def __init__(self, log_dir: Path = None):
        self.log_dir = log_dir or Path("logs")
        self.errors: List[ErrorRecord] = []
        self.logger = get_logger("deployment.errors")
    
    def analyze_logs(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze logs for errors"""
        cutoff = datetime.now() - timedelta(hours=hours)
        error_records = []
        
        log_files = list(self.log_dir.glob("*.log"))
        for log_file in log_files:
            try:
                with open(log_file) as f:
                    for line in f:
                        try:
                            log_entry = json.loads(line)
                            if log_entry.get("level") in ("ERROR", "CRITICAL"):
                                timestamp = datetime.fromisoformat(log_entry.get("timestamp", ""))
                                if timestamp >= cutoff:
                                    error_records.append(ErrorRecord(
                                        timestamp=log_entry.get("timestamp"),
                                        level=log_entry.get("level"),
                                        message=log_entry.get("message"),
                                        module=log_entry.get("module", ""),
                                        function=log_entry.get("function", ""),
                                        traceback=log_entry.get("traceback")
                                    ))
                        except (json.JSONDecodeError, ValueError):
                            continue
            except Exception as e:
                self.logger.error(f"Failed to analyze log file {log_file}: {e}")
        
        self.errors = error_records
        return self._aggregate_errors(error_records)
    
    def _aggregate_errors(self, errors: List[ErrorRecord]) -> Dict[str, Any]:
        """Aggregate error data"""
        if not errors:
            return {
                "total_errors": 0,
                "by_level": {},
                "by_module": {},
                "top_errors": [],
                "timestamp": datetime.now().isoformat()
            }
        
        by_level = defaultdict(int)
        by_module = defaultdict(int)
        by_message = defaultdict(int)
        
        for error in errors:
            by_level[error.level] += 1
            by_module[error.module] += 1
            by_message[error.message] += 1
        
        top_errors = sorted(by_message.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_errors": len(errors),
            "by_level": dict(by_level),
            "by_module": dict(by_module),
            "top_errors": [{"message": msg, "count": count} for msg, count in top_errors],
            "timestamp": datetime.now().isoformat()
        }
    
    def get_error_trend(self, hours: int = 24) -> Dict[str, Any]:
        """Get error trend over time"""
        cutoff = datetime.now() - timedelta(hours=hours)
        period_errors = [
            e for e in self.errors
            if datetime.fromisoformat(e.timestamp) >= cutoff
        ]
        
        # Group by hour
        hourly = defaultdict(int)
        for error in period_errors:
            hour = datetime.fromisoformat(error.timestamp).strftime("%Y-%m-%d %H:00")
            hourly[hour] += 1
        
        return {
            "period_hours": hours,
            "hourly_trend": dict(sorted(hourly.items())),
            "total": len(period_errors)
        }
    
    def generate_report(self, hours: int = 24) -> str:
        """Generate error analysis report"""
        analysis = self.analyze_logs(hours)
        
        report = []
        report.append("=" * 60)
        report.append("MAHA SALES ENGINE V1 - Error Analysis Report")
        report.append("=" * 60)
        report.append(f"Period: Last {hours} hours")
        report.append(f"Total Errors: {analysis.get('total_errors', 0)}")
        report.append("")
        
        if analysis.get("by_level"):
            report.append("Errors by Level:")
            for level, count in analysis["by_level"].items():
                report.append(f"  {level}: {count}")
            report.append("")
        
        if analysis.get("by_module"):
            report.append("Errors by Module:")
            for module, count in sorted(analysis["by_module"].items(), key=lambda x: x[1], reverse=True):
                report.append(f"  {module}: {count}")
            report.append("")
        
        if analysis.get("top_errors"):
            report.append("Top Errors:")
            for i, error in enumerate(analysis["top_errors"], 1):
                report.append(f"  {i}. [{error['count']}x] {error['message'][:100]}")
        
        report.append("=" * 60)
        
        return "\n".join(report)


def main():
    """CLI for error aggregator"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Error aggregator")
    parser.add_argument("--hours", type=int, default=24, help="Hours to analyze")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    aggregator = ErrorAggregator()
    
    if args.json:
        result = aggregator.analyze_logs(args.hours)
        print(json.dumps(result, indent=2))
    else:
        print(aggregator.generate_report(args.hours))


if __name__ == "__main__":
    main()
