#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Uptime Monitor

Tracks system uptime and availability.
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

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.logging_utils import get_logger
from shared.core_engine import get_engine

logger = get_logger("deployment.uptime")


@dataclass
class UptimeRecord:
    """Uptime record"""
    timestamp: str
    status: str
    response_time: float
    error: Optional[str] = None


class UptimeMonitor:
    """Monitors system uptime"""
    
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("data/uptime")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.records: List[UptimeRecord] = []
        self.start_time = datetime.now()
        self.logger = get_logger("deployment.uptime")
    
    def check_uptime(self) -> UptimeRecord:
        """Check current uptime status"""
        try:
            engine = get_engine()
            start = time.time()
            health = engine.get_health()
            response_time = time.time() - start
            
            status = "up" if health.get("status") == "running" else "degraded"
            
            record = UptimeRecord(
                timestamp=datetime.now().isoformat(),
                status=status,
                response_time=response_time
            )
            
            self.records.append(record)
            self._save_record(record)
            
            return record
        except Exception as e:
            record = UptimeRecord(
                timestamp=datetime.now().isoformat(),
                status="down",
                response_time=0,
                error=str(e)
            )
            self.records.append(record)
            self._save_record(record)
            return record
    
    def get_uptime_stats(self, period: str = "24h") -> Dict[str, Any]:
        """Get uptime statistics"""
        now = datetime.now()
        
        if period == "1h":
            start = now - timedelta(hours=1)
        elif period == "24h":
            start = now - timedelta(hours=24)
        elif period == "7d":
            start = now - timedelta(days=7)
        elif period == "30d":
            start = now - timedelta(days=30)
        else:
            start = now - timedelta(hours=24)
        
        period_records = [
            r for r in self.records
            if datetime.fromisoformat(r.timestamp) >= start
        ]
        
        if not period_records:
            return {
                "period": period,
                "status": "no_data",
                "uptime_percent": 0,
                "total_checks": 0
            }
        
        total_checks = len(period_records)
        up_checks = sum(1 for r in period_records if r.status == "up")
        uptime_percent = (up_checks / total_checks * 100) if total_checks > 0 else 0
        
        return {
            "period": period,
            "status": "up" if uptime_percent >= 99 else "degraded" if uptime_percent >= 95 else "down",
            "uptime_percent": round(uptime_percent, 2),
            "total_checks": total_checks,
            "up_checks": up_checks,
            "down_checks": total_checks - up_checks,
            "avg_response_time": sum(r.response_time for r in period_records if r.response_time > 0) / max(up_checks, 1),
            "start_time": self.start_time.isoformat(),
            "current_time": now.isoformat()
        }
    
    def _save_record(self, record: UptimeRecord) -> None:
        """Save uptime record to file"""
        try:
            record_file = self.data_dir / f"uptime-{datetime.now().strftime('%Y%m%d')}.json"
            with open(record_file, "a") as f:
                f.write(json.dumps(record.__dict__) + "\n")
        except Exception as e:
            self.logger.error(f"Failed to save uptime record: {e}")
    
    def get_uptime_report(self) -> Dict[str, Any]:
        """Get comprehensive uptime report"""
        stats_1h = self.get_uptime_stats("1h")
        stats_24h = self.get_uptime_stats("24h")
        stats_7d = self.get_uptime_stats("7d")
        stats_30d = self.get_uptime_stats("30d")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "start_time": self.start_time.isoformat(),
            "uptime": {
                "1h": stats_1h,
                "24h": stats_24h,
                "7d": stats_7d,
                "30d": stats_30d
            },
            "total_records": len(self.records)
        }


def main():
    """CLI for uptime monitor"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Uptime monitor")
    parser.add_argument("--period", default="24h", choices=["1h", "24h", "7d", "30d"])
    parser.add_argument("--check", action="store_true", help="Run single check")
    
    args = parser.parse_args()
    
    monitor = UptimeMonitor()
    
    if args.check:
        record = monitor.check_uptime()
        print(json.dumps(record.__dict__, indent=2))
        sys.exit(0 if record.status == "up" else 1)
    else:
        report = monitor.get_uptime_report()
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
