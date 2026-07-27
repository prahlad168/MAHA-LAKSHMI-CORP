#!/usr/bin/env python3
"""
KILO SALES NODE - Core Orchestrator
Each node is an independent sales unit for a specific market/region.
Communicates with central dashboard via encrypted HTTPS API.
"""

import os
import sys
import json
import time
import threading
import requests
import ssl
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Node configuration
NODE_ID = os.getenv("KILO_NODE_ID", "node-1")
NODE_NAME = os.getenv("KILO_NODE_NAME", "Indonesia Market Node")
DASHBOARD_URL = os.getenv("KILO_DASHBOARD_URL", "https://mahalaksmi.web.id")
API_ENDPOINT = os.getenv("KILO_API_ENDPOINT", "/api/v1/nodes")
AUTH_TOKEN = os.getenv("KILO_AUTH_TOKEN", "")
CERT_PATH = os.getenv("KILO_CERT_PATH", "/etc/ssl/node.crt")
KEY_PATH = os.getenv("KILO_KEY_PATH", "/etc/ssl/node.key")
CA_PATH = os.getenv("KILO_CA_PATH", "/etc/ssl/ca.crt")

# Paths
BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "db" / f"{NODE_ID}.db"
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)


class KiloSalesNode:
    """Main node orchestrator for KILO SALES NODE"""
    
    def __init__(self):
        self.node_id = NODE_ID
        self.node_name = NODE_NAME
        self.dashboard_url = DASHBOARD_URL
        self.running = False
        self.heartbeat_interval = 60  # seconds
        self.report_interval = 86400  # 24 hours
        
        # Load node config
        self.config = self._load_config()
        
        # Initialize components
        self.sales_agent = None
        self.finance_agent = None
        self.market_analyzer = None
        self.reporter = None
        self.api_client = None
        
    def _load_config(self) -> Dict[str, Any]:
        """Load node configuration"""
        config_path = BASE_DIR / "config" / "node.yaml"
        if config_path.exists():
            import yaml
            with open(config_path) as f:
                return yaml.safe_load(f)
        return {
            "node": {"id": NODE_ID, "name": NODE_NAME},
            "sales": {"daily_leads_target": 50, "daily_outreach_target": 100},
            "channels": {"email": {"enabled": True}, "whatsapp": {"enabled": True}}
        }
    
    def _setup_logging(self):
        """Setup logging for node"""
        import logging
        logger = logging.getLogger(f"kilo-node-{NODE_ID}")
        logger.setLevel(logging.INFO)
        
        # File handler
        fh = logging.FileHandler(LOG_DIR / "node.log")
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    def _create_ssl_context(self) -> Optional[ssl.SSLContext]:
        """Create SSL context for mTLS"""
        if not all([CERT_PATH.exists(), KEY_PATH.exists(), CA_PATH.exists()]):
            return None
            
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=CA_PATH)
        context.load_cert_chain(certfile=CERT_PATH, keyfile=KEY_PATH)
        context.check_hostname = True
        return context
    
    def register_with_dashboard(self) -> bool:
        """Register this node with the central dashboard"""
        try:
            payload = {
                "node_id": self.node_id,
                "name": self.node_name,
                "region": self.config.get("node", {}).get("region", "unknown"),
                "market": self.config.get("node", {}).get("market", "unknown"),
                "capabilities": [
                    ch for ch, cfg in self.config.get("channels", {}).items() 
                    if cfg.get("enabled", False)
                ],
                "products": self.config.get("sales", {}).get("products", []),
                "version": "1.0.0"
            }
            
            headers = {
                "Authorization": f"Bearer {AUTH_TOKEN}",
                "Content-Type": "application/json"
            }
            
            ssl_context = self._create_ssl_context()
            response = requests.post(
                f"{self.dashboard_url}/api/v1/nodes/register",
                json=payload,
                headers=headers,
                timeout=30,
                verify=str(CA_PATH) if CA_PATH else True,
                cert=(CERT_PATH, KEY_PATH) if CERT_PATH.exists() else None
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Node {NODE_ID} registered with dashboard")
                return True
            else:
                print(f"❌ Registration failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
    
    def send_heartbeat(self) -> bool:
        """Send heartbeat to dashboard"""
        try:
            import psutil
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_usage = psutil.virtual_memory().percent
        except ImportError:
            cpu_usage = 0.0
            memory_usage = 0.0
        
        payload = {
            "node_id": self.node_id,
            "status": "running" if self.running else "stopped",
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "active_leads": 0,
                "queue_size": 0
            }
        }
        
        try:
            headers = {
                "Authorization": f"Bearer {AUTH_TOKEN}",
                "X-Node-ID": self.node_id,
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.dashboard_url}/api/v1/nodes/heartbeat",
                json=payload,
                headers=headers,
                timeout=10,
                verify=str(CA_PATH) if CA_PATH else True,
                cert=(CERT_PATH, KEY_PATH) if CERT_PATH.exists() else None
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Heartbeat failed: {e}")
            return False
    
    def send_daily_report(self) -> bool:
        """Send daily sales report to dashboard"""
        try:
            # Collect metrics from local database
            metrics = self._collect_metrics()
            
            payload = {
                "node_id": self.node_id,
                "report_date": datetime.now().strftime("%Y-%m-%d"),
                "metrics": metrics,
                "top_products": [],
                "top_channels": [],
                "insights": {}
            }
            
            headers = {
                "Authorization": f"Bearer {AUTH_TOKEN}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.dashboard_url}/api/v1/nodes/report",
                json=payload,
                headers=headers,
                timeout=30,
                verify=str(CA_PATH) if CA_PATH else True,
                cert=(CERT_PATH, KEY_PATH) if CERT_PATH.exists() else None
            )
            
            if response.status_code == 200:
                print(f"✅ Daily report sent for {NODE_ID}")
                return True
            else:
                print(f"❌ Report failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Report error: {e}")
            return False
    
    def _collect_metrics(self) -> Dict[str, Any]:
        """Collect metrics from local database"""
        # This would query the local SQLite database
        # Placeholder for now
        return {
            "leads_generated": 0,
            "outreach_sent": 0,
            "responses_received": 0,
            "proposals_sent": 0,
            "deals_closed": 0,
            "revenue_usd": 0.0,
            "revenue_idr": 0.0,
            "ceo_share_usd": 0.0,
            "ceo_share_idr": 0.0
        }
    
    def poll_commands(self) -> Dict[str, Any]:
        """Poll for commands from dashboard"""
        try:
            headers = {
                "Authorization": f"Bearer {AUTH_TOKEN}",
                "X-Node-ID": self.node_id
            }
            
            since = datetime.now().replace(hour=0, minute=0, second=0).isoformat()
            response = requests.get(
                f"{self.dashboard_url}/api/v1/nodes/commands",
                params={"since": since},
                headers=headers,
                timeout=10,
                verify=str(CA_PATH) if CA_PATH else True,
                cert=(CERT_PATH, KEY_PATH) if CERT_PATH.exists() else None
            )
            
            if response.status_code == 200:
                return response.json()
            return {"commands": []}
            
        except Exception as e:
            print(f"Command poll error: {e}")
            return {"commands": []}
    
    def _heartbeat_loop(self):
        """Background heartbeat loop"""
        while self.running:
            self.send_heartbeat()
            time.sleep(self.heartbeat_interval)
    
    def _report_loop(self):
        """Background daily report loop"""
        while self.running:
            now = datetime.now()
            # Send report at 23:59 local time
            if now.hour == 23 and now.minute == 59:
                self.send_daily_report()
            time.sleep(60)
    
    def _command_loop(self):
        """Background command polling loop"""
        while self.running:
            commands = self.poll_commands()
            for cmd in commands.get("commands", []):
                self._execute_command(cmd)
            time.sleep(30)
    
    def _execute_command(self, command: Dict[str, Any]):
        """Execute command from dashboard"""
        cmd_type = command.get("type")
        params = command.get("params", {})
        
        print(f"📋 Executing command: {cmd_type} - {params}")
        
        if cmd_type == "pause_outreach":
            duration = params.get("duration", 3600)
            print(f"⏸️ Pausing outreach for {duration} seconds")
            # Implement pause logic
            
        elif cmd_type == "adjust_pricing":
            product_id = params.get("product_id")
            new_price = params.get("new_price")
            print(f"💰 Adjusting {product_id} price to {new_price}")
            # Implement pricing logic
            
        elif cmd_type == "send_campaign":
            campaign_type = params.get("campaign_type")
            print(f"📢 Sending campaign: {campaign_type}")
            # Implement campaign logic
    
    def start(self):
        """Start the node"""
        print(f"🚀 Starting KILO SALES NODE: {self.node_id}")
        print(f"📡 Dashboard: {self.dashboard_url}")
        print(f"🔒 Encryption: mTLS + JWT")
        print("=" * 60)
        
        self.running = True
        
        # Register with dashboard
        if not self.register_with_dashboard():
            print("⚠️ Failed to register, retrying in 30s...")
            time.sleep(30)
            self.register_with_dashboard()
        
        # Start background threads
        threading.Thread(target=self._heartbeat_loop, daemon=True).start()
        threading.Thread(target=self._report_loop, daemon=True).start()
        threading.Thread(target=self._command_loop, daemon=True).start()
        
        print("✅ Node started successfully")
        print(f"📊 Dashboard: {self.dashboard_url}/nodes/{self.node_id}")
        
        # Main loop
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down node...")
            self.stop()
    
    def stop(self):
        """Stop the node"""
        self.running = False
        print(f"✅ Node {self.node_id} stopped")
    
    def status(self) -> Dict[str, Any]:
        """Get node status"""
        return {
            "node_id": self.node_id,
            "name": self.node_name,
            "status": "running" if self.running else "stopped",
            "dashboard_url": self.dashboard_url,
            "uptime": "N/A"
        }


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="KILO SALES NODE")
    parser.add_argument("command", choices=["start", "stop", "status", "register"])
    parser.add_argument("--node-id", default=NODE_ID, help="Node ID")
    parser.add_argument("--dashboard", default=DASHBOARD_URL, help="Dashboard URL")
    
    args = parser.parse_args()
    
    # Override env vars with args
    os.environ["KILO_NODE_ID"] = args.node_id
    os.environ["KILO_DASHBOARD_URL"] = args.dashboard
    
    node = KiloSalesNode()
    
    if args.command == "start":
        node.start()
    elif args.command == "stop":
        node.stop()
    elif args.command == "status":
        print(json.dumps(node.status(), indent=2))
    elif args.command == "register":
        success = node.register_with_dashboard()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
