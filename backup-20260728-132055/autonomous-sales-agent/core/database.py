#!/usr/bin/env python3
"""
💾 REAL-TIME DATABASE LAYER - MAHA LAKSHMI
Stores actual transactions, leads, and payouts
CEO reports are based on REAL data, not estimates
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import os

# ============== DATABASE PATH ==============
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "maha_lakshmi.db")

# ============== DATA MODELS ==============
@dataclass
class Lead:
    id: str
    name: str
    email: str
    phone: str
    company: str
    industry: str
    country: str
    language: str
    source: str
    status: str = "new"
    score: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_contact: Optional[str] = None
    followup_count: int = 0
    notes: str = ""

@dataclass
class Transaction:
    id: str
    gateway: str
    customer_email: str
    customer_name: str
    amount: float
    currency: str
    fee_amount: float
    net_amount: float
    product_id: str
    status: str = "pending"
    payment_method: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    metadata: str = ""

@dataclass
class Payout:
    id: str
    amount: float
    currency: str
    destination: str
    destination_type: str
    status: str = "pending"
    fee_amount: float = 0.0
    net_amount: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    reference: str = ""

@dataclass
class Report:
    id: str
    report_type: str
    date: str
    data: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

# ============== DATABASE MANAGER ==============
class RealTimeDatabase:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Leads table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                company TEXT,
                industry TEXT,
                country TEXT,
                language TEXT,
                source TEXT,
                status TEXT DEFAULT 'new',
                score INTEGER DEFAULT 0,
                created_at TEXT,
                last_contact TEXT,
                followup_count INTEGER DEFAULT 0,
                notes TEXT
            )
        """)
        
        # Transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                gateway TEXT NOT NULL,
                customer_email TEXT,
                customer_name TEXT,
                amount REAL NOT NULL,
                currency TEXT NOT NULL,
                fee_amount REAL DEFAULT 0.0,
                net_amount REAL NOT NULL,
                product_id TEXT,
                status TEXT DEFAULT 'pending',
                payment_method TEXT,
                created_at TEXT,
                completed_at TEXT,
                metadata TEXT
            )
        """)
        
        # Payouts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payouts (
                id TEXT PRIMARY KEY,
                amount REAL NOT NULL,
                currency TEXT NOT NULL,
                destination TEXT NOT NULL,
                destination_type TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                fee_amount REAL DEFAULT 0.0,
                net_amount REAL NOT NULL,
                created_at TEXT,
                completed_at TEXT,
                reference TEXT
            )
        """)
        
        # Reports table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                report_type TEXT NOT NULL,
                date TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TEXT
            )
        """)
        
        # Outreach log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS outreach_log (
                id TEXT PRIMARY KEY,
                lead_id TEXT,
                channel TEXT NOT NULL,
                template_type TEXT,
                content TEXT,
                status TEXT DEFAULT 'sent',
                sent_at TEXT,
                response_received INTEGER DEFAULT 0,
                response_at TEXT,
                FOREIGN KEY (lead_id) REFERENCES leads (id)
            )
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_payouts_date ON payouts(created_at)")
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # ========== LEAD MANAGEMENT ==========
    def insert_lead(self, lead: Lead) -> bool:
        """Insert new lead"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO leads 
                (id, name, email, phone, company, industry, country, language, source, status, score, created_at, last_contact, followup_count, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                lead.id, lead.name, lead.email, lead.phone, lead.company,
                lead.industry, lead.country, lead.language, lead.source,
                lead.status, lead.score, lead.created_at, lead.last_contact,
                lead.followup_count, lead.notes
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"DB Error inserting lead: {e}")
            return False
    
    def get_leads_by_status(self, status: str) -> List[Dict]:
        """Get leads by status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leads WHERE status = ?", (status,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def update_lead_status(self, lead_id: str, status: str):
        """Update lead status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE leads SET status = ? WHERE id = ?", (status, lead_id))
        conn.commit()
        conn.close()
    
    def get_lead_stats(self) -> Dict:
        """Get lead statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total leads
        cursor.execute("SELECT COUNT(*) FROM leads")
        total = cursor.fetchone()[0]
        
        # By status
        cursor.execute("SELECT status, COUNT(*) FROM leads GROUP BY status")
        by_status = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Today's leads
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT COUNT(*) FROM leads WHERE date(created_at) = ?", (today,))
        today_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total": total,
            "by_status": by_status,
            "today": today_count
        }
    
    # ========== TRANSACTION MANAGEMENT ==========
    def insert_transaction(self, transaction: Transaction) -> bool:
        """Insert new transaction"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO transactions 
                (id, gateway, customer_email, customer_name, amount, currency, fee_amount, net_amount, product_id, status, payment_method, created_at, completed_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                transaction.id, transaction.gateway, transaction.customer_email,
                transaction.customer_name, transaction.amount, transaction.currency,
                transaction.fee_amount, transaction.net_amount, transaction.product_id,
                transaction.status, transaction.payment_method, transaction.created_at,
                transaction.completed_at, transaction.metadata
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"DB Error inserting transaction: {e}")
            return False
    
    def update_transaction_status(self, transaction_id: str, status: str, completed_at: Optional[str] = None):
        """Update transaction status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if completed_at:
            cursor.execute(
                "UPDATE transactions SET status = ?, completed_at = ? WHERE id = ?",
                (status, completed_at, transaction_id)
            )
        else:
            cursor.execute(
                "UPDATE transactions SET status = ? WHERE id = ?",
                (status, transaction_id)
            )
        
        conn.commit()
        conn.close()
    
    def get_transactions_by_status(self, status: str) -> List[Dict]:
        """Get transactions by status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions WHERE status = ?", (status,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_revenue_stats(self) -> Dict:
        """Get real revenue statistics from database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total revenue (completed transactions)
        cursor.execute("SELECT SUM(net_amount) FROM transactions WHERE status = 'completed'")
        total_revenue = cursor.fetchone()[0] or 0.0
        
        # Today's revenue
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute(
            "SELECT SUM(net_amount) FROM transactions WHERE status = 'completed' AND date(completed_at) = ?",
            (today,)
        )
        today_revenue = cursor.fetchone()[0] or 0.0
        
        # Total transactions
        cursor.execute("SELECT COUNT(*) FROM transactions")
        total_transactions = cursor.fetchone()[0]
        
        # Completed transactions
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE status = 'completed'")
        completed_transactions = cursor.fetchone()[0]
        
        # Pending transactions
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE status = 'pending'")
        pending_transactions = cursor.fetchone()[0]
        
        # By currency
        cursor.execute(
            "SELECT currency, SUM(net_amount), COUNT(*) FROM transactions WHERE status = 'completed' GROUP BY currency"
        )
        by_currency = {}
        for row in cursor.fetchall():
            by_currency[row[0]] = {"amount": row[1], "count": row[2]}
        
        # By gateway
        cursor.execute(
            "SELECT gateway, SUM(net_amount), COUNT(*) FROM transactions WHERE status = 'completed' GROUP BY gateway"
        )
        by_gateway = {}
        for row in cursor.fetchall():
            by_gateway[row[0]] = {"amount": row[1], "count": row[2]}
        
        conn.close()
        
        return {
            "total_revenue": total_revenue,
            "today_revenue": today_revenue,
            "total_transactions": total_transactions,
            "completed_transactions": completed_transactions,
            "pending_transactions": pending_transactions,
            "by_currency": by_currency,
            "by_gateway": by_gateway,
            "ceo_share": total_revenue * 0.8,
            "ceo_share_today": today_revenue * 0.8
        }
    
    # ========== PAYOUT MANAGEMENT ==========
    def insert_payout(self, payout: Payout) -> bool:
        """Insert new payout"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO payouts 
                (id, amount, currency, destination, destination_type, status, fee_amount, net_amount, created_at, completed_at, reference)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                payout.id, payout.amount, payout.currency, payout.destination,
                payout.destination_type, payout.status, payout.fee_amount,
                payout.net_amount, payout.created_at, payout.completed_at,
                payout.reference
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"DB Error inserting payout: {e}")
            return False
    
    def get_pending_payouts(self) -> List[Dict]:
        """Get pending payouts"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM payouts WHERE status = 'pending'")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_payout_stats(self) -> Dict:
        """Get payout statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total payouts
        cursor.execute("SELECT COUNT(*), SUM(net_amount) FROM payouts")
        row = cursor.fetchone()
        total_payouts = row[0]
        total_payout_amount = row[1] or 0.0
        
        # Completed payouts
        cursor.execute("SELECT COUNT(*), SUM(net_amount) FROM payouts WHERE status = 'completed'")
        row = cursor.fetchone()
        completed_payouts = row[0]
        completed_amount = row[1] or 0.0
        
        # Pending payouts
        cursor.execute("SELECT COUNT(*), SUM(net_amount) FROM payouts WHERE status = 'pending'")
        row = cursor.fetchone()
        pending_payouts = row[0]
        pending_amount = row[1] or 0.0
        
        # Today's payouts
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute(
            "SELECT COUNT(*), SUM(net_amount) FROM payouts WHERE date(created_at) = ?",
            (today,)
        )
        row = cursor.fetchone()
        today_payouts = row[0]
        today_amount = row[1] or 0.0
        
        conn.close()
        
        return {
            "total_payouts": total_payouts,
            "total_amount": total_payout_amount,
            "completed_payouts": completed_payouts,
            "completed_amount": completed_amount,
            "pending_payouts": pending_payouts,
            "pending_amount": pending_amount,
            "today_payouts": today_payouts,
            "today_amount": today_amount
        }
    
    # ========== OUTREACH LOG ==========
    def log_outreach(self, lead_id: str, channel: str, template_type: str, content: str):
        """Log outreach action"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO outreach_log (id, lead_id, channel, template_type, content, status, sent_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                f"OUTREACH-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                lead_id, channel, template_type, content, "sent",
                datetime.now().isoformat()
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"DB Error logging outreach: {e}")
    
    def get_outreach_stats(self) -> Dict:
        """Get outreach statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total outreach
        cursor.execute("SELECT COUNT(*) FROM outreach_log")
        total = cursor.fetchone()[0]
        
        # By channel
        cursor.execute("SELECT channel, COUNT(*) FROM outreach_log GROUP BY channel")
        by_channel = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Today's outreach
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT COUNT(*) FROM outreach_log WHERE date(sent_at) = ?", (today,))
        today_count = cursor.fetchone()[0]
        
        # Responses
        cursor.execute("SELECT COUNT(*) FROM outreach_log WHERE response_received = 1")
        responses = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total": total,
            "by_channel": by_channel,
            "today": today_count,
            "responses": responses
        }
    
    # ========== REPORTS ==========
    def save_report(self, report: Report) -> bool:
        """Save report"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO reports (id, report_type, date, data, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (report.id, report.report_type, report.date, report.data, report.created_at))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"DB Error saving report: {e}")
            return False
    
    def get_latest_report(self, report_type: str) -> Optional[Dict]:
        """Get latest report of a type"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM reports WHERE report_type = ? ORDER BY created_at DESC LIMIT 1",
            (report_type,)
        )
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    # ========== REAL-TIME DASHBOARD DATA ==========
    def get_dashboard_data(self) -> Dict:
        """Get real-time data for CEO dashboard"""
        revenue_stats = self.get_revenue_stats()
        lead_stats = self.get_lead_stats()
        outreach_stats = self.get_outreach_stats()
        payout_stats = self.get_payout_stats()
        
        # Get today's date
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Get recent transactions
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM transactions ORDER BY created_at DESC LIMIT 10"
        )
        recent_transactions = [dict(row) for row in cursor.fetchall()]
        
        # Get recent payouts
        cursor.execute(
            "SELECT * FROM payouts ORDER BY created_at DESC LIMIT 5"
        )
        recent_payouts = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "date": today,
            "revenue": revenue_stats,
            "leads": lead_stats,
            "outreach": outreach_stats,
            "payouts": payout_stats,
            "recent_transactions": recent_transactions,
            "recent_payouts": recent_payouts,
            "ceo_share": revenue_stats["ceo_share"],
            "ceo_share_today": revenue_stats["ceo_share_today"]
        }
