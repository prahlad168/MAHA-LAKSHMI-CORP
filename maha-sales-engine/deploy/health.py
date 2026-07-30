#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Health Check Endpoints

Production health check endpoints for load balancers and monitoring.
"""

import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.core_engine import get_engine
from shared.health import health_monitor, get_health_monitor
from shared.database import DatabaseManager
from shared.logging_utils import get_logger

logger = get_logger("deployment.health")


class HealthCheckServer:
    """Simple HTTP health check server"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        self.host = host
        self.port = port
        self.engine = get_engine()
        self.health_monitor = get_health_monitor()
    
    def start(self):
        """Start health check server"""
        try:
            from http.server import HTTPServer, BaseHTTPRequestHandler
            import threading
            
            class HealthHandler(BaseHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    self.health_server = self
                    super().__init__(*args, **kwargs)
                
                def log_message(self, format, *args):
                    pass
                
                def do_GET(self):
                    path = self.path.split('?')[0]
                    
                    if path == '/health':
                        self._send_response(self._get_health())
                    elif path == '/ready':
                        self._send_response(self._get_readiness())
                    elif path == '/metrics':
                        self._send_response(self._get_metrics())
                    else:
                        self._send_response({"status": "not_found"}, 404)
                
                def _send_response(self, data: Dict[str, Any], status: int = 200):
                    self.send_response(status)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(data).encode())
                
                def _get_health(self) -> Dict[str, Any]:
                    """Get health status"""
                    try:
                        engine_health = self.engine.get_health()
                        return {
                            "status": "healthy" if engine_health.get("status") == "running" else "unhealthy",
                            "timestamp": datetime.now().isoformat(),
                            "engine": engine_health
                        }
                    except Exception as e:
                        return {
                            "status": "unhealthy",
                            "error": str(e),
                            "timestamp": datetime.now().isoformat()
                        }
                
                def _get_readiness(self) -> Dict[str, Any]:
                    """Get readiness status"""
                    try:
                        # Check if application is ready to serve traffic
                        db_health = self.health_monitor.check_component("database")
                        return {
                            "ready": db_health.get("status") == "healthy",
                            "timestamp": datetime.now().isoformat(),
                            "checks": {
                                "database": db_health
                            }
                        }
                    except Exception as e:
                        return {
                            "ready": False,
                            "error": str(e),
                            "timestamp": datetime.now().isoformat()
                        }
                
                def _get_metrics(self) -> Dict[str, Any]:
                    """Get application metrics"""
                    try:
                        metrics = self.engine.get_status()
                        return metrics
                    except Exception as e:
                        return {"error": str(e)}
            
            server = HTTPServer((self.host, self.port), HealthHandler)
            server.serve_forever()
        except Exception as e:
            logger.error(f"Failed to start health check server: {e}")
            raise


def check_health() -> Dict[str, Any]:
    """Simple health check function"""
    try:
        engine = get_engine()
        health = engine.get_health()
        return {
            "status": "healthy" if health.get("status") == "running" else "unhealthy",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Health check server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--check", action="store_true", help="Run single health check")
    
    args = parser.parse_args()
    
    if args.check:
        result = check_health()
        print(json.dumps(result, indent=2))
        sys.exit(0 if result.get("status") == "healthy" else 1)
    else:
        server = HealthCheckServer(args.host, args.port)
        server.start()
