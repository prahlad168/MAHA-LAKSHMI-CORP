#!/usr/bin/env python3
"""
KILO SALES NODE - Node Registry
Central registry for managing all sales nodes.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

# Registry storage (use PostgreSQL/Redis in production)
REGISTRY_FILE = Path(__file__).parent.parent / "registry" / "nodes.json"
REGISTRY_FILE.parent.mkdir(exist_ok=True)


class NodeRegistry:
    """Central registry for all KILO SALES NODEs"""
    
    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.load()
    
    def load(self):
        """Load registry from file"""
        if REGISTRY_FILE.exists():
            with open(REGISTRY_FILE) as f:
                self.nodes = json.load(f)
    
    def save(self):
        """Save registry to file"""
        with open(REGISTRY_FILE, "w") as f:
            json.dump(self.nodes, f, indent=2)
    
    def register(self, node_info: Dict[str, Any]) -> bool:
        """Register a new node"""
        node_id = node_info["node_id"]
        
        if node_id in self.nodes:
            return False
        
        self.nodes[node_id] = {
            "info": node_info,
            "registered_at": datetime.now().isoformat(),
            "last_heartbeat": None,
            "status": "online",
            "metrics": {},
            "reports": []
        }
        
        self.save()
        print(f"✅ Node registered: {node_id}")
        return True
    
    def update_heartbeat(self, node_id: str, metrics: Dict[str, Any]):
        """Update node heartbeat"""
        if node_id not in self.nodes:
            return False
        
        self.nodes[node_id]["last_heartbeat"] = datetime.now().isoformat()
        self.nodes[node_id]["metrics"] = metrics
        self.save()
        return True
    
    def add_report(self, node_id: str, report: Dict[str, Any]):
        """Add daily report from node"""
        if node_id not in self.nodes:
            return False
        
        self.nodes[node_id]["reports"].append({
            "date": report.get("report_date"),
            "data": report,
            "received_at": datetime.now().isoformat()
        })
        
        # Keep only last 30 days of reports
        if len(self.nodes[node_id]["reports"]) > 30:
            self.nodes[node_id]["reports"] = self.nodes[node_id]["reports"][-30:]
        
        self.save()
        return True
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get node by ID"""
        return self.nodes.get(node_id)
    
    def get_all_nodes(self) -> List[Dict[str, Any]]:
        """Get all registered nodes"""
        return [
            {
                "node_id": node_id,
                "name": data["info"]["name"],
                "region": data["info"]["region"],
                "market": data["info"]["market"],
                "status": data["status"],
                "last_heartbeat": data["last_heartbeat"],
                "registered_at": data["registered_at"]
            }
            for node_id, data in self.nodes.items()
        ]
    
    def get_online_nodes(self) -> List[Dict[str, Any]]:
        """Get nodes that have sent heartbeat recently"""
        now = datetime.now()
        threshold = timedelta(minutes=15)
        
        online_nodes = []
        for node_id, data in self.nodes.items():
            if data["last_heartbeat"]:
                last_hb = datetime.fromisoformat(data["last_heartbeat"])
                if now - last_hb < threshold:
                    online_nodes.append({
                        "node_id": node_id,
                        "name": data["info"]["name"],
                        "region": data["info"]["region"],
                        "status": "online",
                        "last_heartbeat": data["last_heartbeat"]
                    })
        
        return online_nodes
    
    def get_offline_nodes(self) -> List[Dict[str, Any]]:
        """Get nodes that have not sent heartbeat recently"""
        now = datetime.now()
        threshold = timedelta(minutes=15)
        
        offline_nodes = []
        for node_id, data in self.nodes.items():
            if not data["last_heartbeat"]:
                offline_nodes.append({
                    "node_id": node_id,
                    "name": data["info"]["name"],
                    "status": "offline",
                    "reason": "Never connected"
                })
                continue
            
            last_hb = datetime.fromisoformat(data["last_heartbeat"])
            if now - last_hb >= threshold:
                offline_nodes.append({
                    "node_id": node_id,
                    "name": data["info"]["name"],
                    "status": "offline",
                    "last_heartbeat": data["last_heartbeat"],
                    "reason": f"Last seen {last_hb.strftime('%Y-%m-%d %H:%M:%S')}"
                })
        
        return offline_nodes
    
    def get_aggregated_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics across all nodes"""
        total_leads = 0
        total_outreach = 0
        total_responses = 0
        total_deals = 0
        total_revenue_usd = 0.0
        total_revenue_idr = 0.0
        
        for node_id, data in self.nodes.items():
            metrics = data.get("metrics", {})
            total_leads += metrics.get("active_leads", 0)
            total_outreach += metrics.get("outreach_sent", 0)
            total_responses += metrics.get("responses_received", 0)
            total_deals += metrics.get("deals_closed", 0)
            total_revenue_usd += metrics.get("revenue_usd", 0.0)
            total_revenue_idr += metrics.get("revenue_idr", 0.0)
        
        return {
            "total_nodes": len(self.nodes),
            "online_nodes": len(self.get_online_nodes()),
            "total_leads": total_leads,
            "total_outreach": total_outreach,
            "total_responses": total_responses,
            "total_deals": total_deals,
            "total_revenue_usd": total_revenue_usd,
            "total_revenue_idr": total_revenue_idr,
            "ceo_share_usd": total_revenue_usd * 0.8,
            "ceo_share_idr": total_revenue_idr * 0.8
        }
    
    def get_node_rankings(self) -> List[Dict[str, Any]]:
        """Get nodes ranked by revenue"""
        rankings = []
        for node_id, data in self.nodes.items():
            metrics = data.get("metrics", {})
            rankings.append({
                "node_id": node_id,
                "name": data["info"]["name"],
                "revenue_usd": metrics.get("revenue_usd", 0.0),
                "deals_closed": metrics.get("deals_closed", 0),
                "conversion_rate": metrics.get("conversion_rate", 0.0)
            })
        
        rankings.sort(key=lambda x: x["revenue_usd"], reverse=True)
        return rankings


def main():
    """Test registry"""
    registry = NodeRegistry()
    
    # Register test node
    registry.register({
        "node_id": "node-1",
        "name": "Indonesia Market Node",
        "region": "id",
        "market": "Indonesia",
        "capabilities": ["email", "whatsapp"],
        "products": ["social-media-kit"],
        "version": "1.0.0"
    })
    
    # Update heartbeat
    registry.update_heartbeat("node-1", {
        "cpu_usage": 0.0,
        "memory_usage": 8.5,
        "active_leads": 45,
        "outreach_sent": 120,
        "revenue_usd": 350.0
    })
    
    # Get stats
    print("All nodes:", registry.get_all_nodes())
    print("Online nodes:", registry.get_online_nodes())
    print("Aggregated metrics:", registry.get_aggregated_metrics())


if __name__ == "__main__":
    main()
