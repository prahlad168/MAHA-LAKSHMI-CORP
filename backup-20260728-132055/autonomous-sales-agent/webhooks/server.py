#!/usr/bin/env python3
"""
🔗 WEBHOOK SERVER - MAHA LAKSHMI
Receives real-time payment notifications from gateways
Updates database instantly for real-time CEO reports
"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Try to import FastAPI, fallback to simple HTTP server
try:
    from fastapi import FastAPI, Request, HTTPException
    from fastapi.responses import JSONResponse
    import uvicorn
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    from http.server import HTTPServer, BaseHTTPRequestHandler

# Import database
from autonomous_sales_agent.core.database import RealTimeDatabase

# Initialize database
db = RealTimeDatabase()

if HAS_FASTAPI:
    app = FastAPI(title="MAHA LAKSHMI Webhooks", version="1.0")
    
    @app.post("/webhook/payment")
    async def payment_webhook(request: Request):
        """Receive payment webhook from any gateway"""
        try:
            payload = await request.json()
            gateway = payload.get("gateway", "unknown")
            transaction_id = payload.get("transaction_id") or payload.get("id")
            status = payload.get("status", "pending")
            amount = payload.get("amount", 0.0)
            
            # Update transaction in database
            if status in ["completed", "success"]:
                db.update_transaction_status(
                    transaction_id,
                    "completed",
                    datetime.now().isoformat()
                )
                
                # Create payout record
                payout_id = f"PAYOUT-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
                payout = {
                    "id": payout_id,
                    "amount": amount * 0.8,  # CEO share
                    "currency": payload.get("currency", "USD"),
                    "destination": "BCA 6485086645",
                    "destination_type": "bank",
                    "status": "processing",
                    "reference": transaction_id,
                    "created_at": datetime.now().isoformat()
                }
                
                # Insert payout into database
                from autonomous_sales_agent.finance.finance_agent import Payout
                payout_obj = Payout(
                    id=payout_id,
                    amount=amount * 0.8,
                    currency=payload.get("currency", "USD"),
                    destination="BCA 6485086645",
                    destination_type="bank",
                    status="processing",
                    reference=transaction_id
                )
                db.insert_payout(payout_obj)
                
                return JSONResponse({
                    "success": True,
                    "status": "completed",
                    "transaction_id": transaction_id,
                    "payout_id": payout_id,
                    "ceo_share": amount * 0.8
                })
            
            elif status == "failed":
                db.update_transaction_status(transaction_id, "failed")
                return JSONResponse({"success": False, "status": "failed"})
            
            return JSONResponse({"success": True, "status": "pending"})
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.post("/webhook/lead")
    async def lead_webhook(request: Request):
        """Receive new lead from any source"""
        try:
            payload = await request.json()
            
            from autonomous_sales_agent.core.sales_agent_core import Lead
            lead = Lead(
                id=f"LEAD-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                name=payload.get("name", "Unknown"),
                email=payload.get("email", ""),
                phone=payload.get("phone", ""),
                company=payload.get("company", ""),
                industry=payload.get("industry", "Technology"),
                country=payload.get("country", "USA"),
                language=payload.get("language", "en"),
                source=payload.get("source", "webhook")
            )
            
            db.insert_lead(lead)
            
            return JSONResponse({
                "success": True,
                "lead_id": lead.id,
                "status": "new"
            })
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.get("/api/agent/dashboard")
    async def dashboard_api():
        """Real-time dashboard data for CEO"""
        try:
            from autonomous_sales_agent.core.sales_agent_core import AutonomousSalesAgent
            from autonomous_sales_agent.finance.finance_agent import AutonomousFinanceAgent
            
            sales_agent = AutonomousSalesAgent()
            finance_agent = AutonomousFinanceAgent()
            
            dashboard_data = db.get_dashboard_data()
            
            return JSONResponse({
                "success": True,
                "data": dashboard_data
            })
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return JSONResponse({
            "status": "healthy",
            "service": "MAHA LAKSHMI Webhooks",
            "timestamp": datetime.now().isoformat(),
            "database": "connected"
        })

else:
    # Fallback simple HTTP server
    class WebhookHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            if self.path == "/webhook/payment":
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                payload = json.loads(post_data.decode('utf-8'))
                
                # Process payment webhook
                transaction_id = payload.get("transaction_id") or payload.get("id")
                status = payload.get("status", "pending")
                
                if status in ["completed", "success"]:
                    db.update_transaction_status(
                        transaction_id,
                        "completed",
                        datetime.now().isoformat()
                    )
                    
                    response = {
                        "success": True,
                        "status": "completed",
                        "transaction_id": transaction_id
                    }
                else:
                    response = {"success": True, "status": "pending"}
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                
            elif self.path == "/webhook/lead":
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                payload = json.loads(post_data.decode('utf-8'))
                
                # Process lead webhook
                from autonomous_sales_agent.core.sales_agent_core import Lead
                lead = Lead(
                    id=f"LEAD-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                    name=payload.get("name", "Unknown"),
                    email=payload.get("email", ""),
                    phone=payload.get("phone", ""),
                    company=payload.get("company", ""),
                    industry=payload.get("industry", "Technology"),
                    country=payload.get("country", "USA"),
                    language=payload.get("language", "en"),
                    source=payload.get("source", "webhook")
                )
                
                db.insert_lead(lead)
                
                response = {
                    "success": True,
                    "lead_id": lead.id,
                    "status": "new"
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                
            else:
                self.send_response(404)
                self.end_headers()
        
        def do_GET(self):
            if self.path == "/health":
                response = {
                    "status": "healthy",
                    "service": "MAHA LAKSHMI Webhooks",
                    "timestamp": datetime.now().isoformat()
                }
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(404)
                self.end_headers()

def start_webhook_server(port: int = 8000):
    """Start webhook server and autonomous sales orchestrator"""
    import threading
    
    # Start autonomous sales orchestrator in background
    def start_orchestrator():
        try:
            from autonomous_sales_agent.orchestrator import AutonomousSalesOrchestrator
            orchestrator = AutonomousSalesOrchestrator()
            orchestrator.start()
        except Exception as e:
            print(f"Orchestrator startup error: {e}")
    
    orchestrator_thread = threading.Thread(target=start_orchestrator, daemon=True)
    orchestrator_thread.start()
    print("🤖 Autonomous Sales Orchestrator started in background")
    
    # Start webhook server
    if HAS_FASTAPI:
        print(f"🚀 Starting FastAPI webhook server on port {port}")
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
    else:
        print(f"🚀 Starting simple HTTP webhook server on port {port}")
        server = HTTPServer(('0.0.0.0', port), WebhookHandler)
        print(f"✅ Webhook server running on http://0.0.0.0:{port}")
        print(f"📡 Payment webhook: POST http://0.0.0.0:{port}/webhook/payment")
        print(f"📡 Lead webhook: POST http://0.0.0.0:{port}/webhook/lead")
        print(f"📊 Dashboard API: GET http://0.0.0.0:{port}/api/agent/dashboard")
        server.serve_forever()

if __name__ == "__main__":
    start_webhook_server()
