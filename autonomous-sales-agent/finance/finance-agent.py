#!/usr/bin/env python3
"""
💰 AUTONOMOUS FINANCE AGENT - MAHA LAKSHMI
Handles ALL payment gateway operations automatically

CEO RECEIVES ONLY:
- Daily revenue reports
- Transfer confirmations
- Financial summaries

AGENT HANDLES:
- Payment gateway setup and configuration
- Transaction processing and reconciliation
- Currency conversion and routing
- Fee optimization
- Payout execution to CEO
- Compliance and record keeping
"""

import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import database with fallback
try:
    from autonomous_sales_agent.core.database import RealTimeDatabase
except ImportError:
    try:
        from core.database import RealTimeDatabase
    except ImportError:
        RealTimeDatabase = None

# ============== PAYMENT GATEWAYS ==============
class PaymentGateway(Enum):
    STRIPE = "stripe"
    PAYPAL = "paypal"
    WISE = "wise"
    CRYPTO = "crypto"
    MIDTRANS = "midtrans"
    DANA = "dana"
    OVO = "ovo"
    GOPAY = "gopay"
    BCA = "bca"
    USDT_TRC20 = "usdt_trc20"

@dataclass
class PaymentConfig:
    gateway: PaymentGateway
    enabled: bool
    api_key: str = ""
    secret_key: str = ""
    webhook_url: str = ""
    supported_currencies: List[str] = field(default_factory=list)
    supported_countries: List[str] = field(default_factory=list)
    fee_percentage: float = 0.0
    fee_fixed: float = 0.0
    settlement_currency: str = "USD"
    auto_payout: bool = True
    payout_destination: str = ""
    daily_limit: float = 10000.0
    monthly_limit: float = 300000.0

@dataclass
class Transaction:
    id: str
    gateway: PaymentGateway
    customer_email: str
    customer_name: str
    amount: float
    currency: str
    fee_amount: float
    net_amount: float
    status: str = "pending"  # pending, completed, failed, refunded
    product_id: str = ""
    invoice_url: str = ""
    receipt_url: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    metadata: Dict = field(default_factory=dict)

@dataclass
class Payout:
    id: str
    amount: float
    currency: str
    destination: str
    destination_type: str  # bank, crypto, ewallet
    status: str = "pending"
    fee_amount: float = 0.0
    net_amount: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    reference: str = ""

# ============== FINANCE AGENT ==============
class AutonomousFinanceAgent:
    def __init__(self):
        self.db = RealTimeDatabase() if RealTimeDatabase else None
        self.gateways: Dict[PaymentGateway, PaymentConfig] = {}
        self.ceo_bank_account = {
            "bank": "BCA",
            "account": "6485086645",
            "name": "i Made Purna Ananda",
            "currency": "IDR"
        }
        self.ceo_crypto_wallet = {
            "network": "TRC20",
            "address": "TNFs1SP2C8HxGSJkSH3hJamf8ukgtnW7U6",
            "currency": "USDT"
        }
        self.fx_rates = {
            "USD_IDR": 16000.0,
            "EUR_IDR": 17500.0,
            "GBP_IDR": 20500.0,
            "SGD_IDR": 12000.0,
            "AUD_IDR": 10500.0,
            "USDT_IDR": 16000.0
        }
        self.fee_structures = {
            PaymentGateway.STRIPE: {"percentage": 0.029, "fixed": 0.30},
            PaymentGateway.PAYPAL: {"percentage": 0.039, "fixed": 0.49},
            PaymentGateway.WISE: {"percentage": 0.015, "fixed": 1.50},
            PaymentGateway.MIDTRANS: {"percentage": 0.025, "fixed": 0.25},
            PaymentGateway.CRYPTO: {"percentage": 0.01, "fixed": 1.00}
        }
        self.initialize_gateways()
    
    def initialize_gateways(self):
        """Initialize payment gateway configurations"""
        self.gateways[PaymentGateway.STRIPE] = PaymentConfig(
            gateway=PaymentGateway.STRIPE,
            enabled=True,
            supported_currencies=["USD", "EUR", "GBP", "SGD", "AUD"],
            supported_countries=["US", "UK", "AU", "SG", "DE", "FR", "global"],
            fee_percentage=0.029,
            fee_fixed=0.30,
            settlement_currency="USD",
            auto_payout=True,
            payout_destination="stripe_balance",
            daily_limit=50000.0,
            monthly_limit=1000000.0
        )
        
        self.gateways[PaymentGateway.PAYPAL] = PaymentConfig(
            gateway=PaymentGateway.PAYPAL,
            enabled=True,
            supported_currencies=["USD", "EUR", "GBP"],
            supported_countries=["US", "UK", "EU", "global"],
            fee_percentage=0.039,
            fee_fixed=0.49,
            settlement_currency="USD",
            auto_payout=True,
            payout_destination="paypal_balance",
            daily_limit=10000.0,
            monthly_limit=300000.0
        )
        
        self.gateways[PaymentGateway.WISE] = PaymentConfig(
            gateway=PaymentGateway.WISE,
            enabled=True,
            supported_currencies=["USD", "EUR", "GBP", "SGD", "AUD", "IDR"],
            supported_countries=["US", "UK", "EU", "SG", "AU", "ID"],
            fee_percentage=0.015,
            fee_fixed=1.50,
            settlement_currency="USD",
            auto_payout=True,
            payout_destination="wise_balance",
            daily_limit=100000.0,
            monthly_limit=2000000.0
        )
        
        self.gateways[PaymentGateway.CRYPTO] = PaymentConfig(
            gateway=PaymentGateway.CRYPTO,
            enabled=True,
            supported_currencies=["USDT", "BTC", "ETH"],
            supported_countries=["global"],
            fee_percentage=0.01,
            fee_fixed=1.00,
            settlement_currency="USDT",
            auto_payout=True,
            payout_destination=self.ceo_crypto_wallet["address"],
            daily_limit=50000.0,
            monthly_limit=1000000.0
        )
        
        self.gateways[PaymentGateway.MIDTRANS] = PaymentConfig(
            gateway=PaymentGateway.MIDTRANS,
            enabled=True,
            supported_currencies=["IDR"],
            supported_countries=["ID"],
            fee_percentage=0.025,
            fee_fixed=0.25,
            settlement_currency="IDR",
            auto_payout=True,
            payout_destination=self.ceo_bank_account["account"],
            daily_limit=50000000.0,
            monthly_limit=500000000.0
        )
    
    # ========== PAYMENT PROCESSING ==========
    def create_payment_link(self, product_id: str, amount: float, currency: str, 
                           customer_email: str, customer_name: str) -> Dict:
        """Create payment link for customer"""
        # Select best gateway based on currency and country
        gateway = self.select_best_gateway(currency, customer_email)
        
        if not gateway:
            return {"success": False, "error": "No suitable payment gateway"}
        
        config = self.gateways[gateway]
        
        # Calculate fees
        fee = self.calculate_fee(gateway, amount)
        net_amount = amount - fee
        
        # Create payment record
        transaction = Transaction(
            id=f"TXN-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            gateway=gateway,
            customer_email=customer_email,
            customer_name=customer_name,
            amount=amount,
            currency=currency,
            fee_amount=fee,
            net_amount=net_amount,
            product_id=product_id,
            status="pending",
            payment_method=gateway.value
        )
        
        # Save to database
        self.db.insert_transaction(transaction)
        
        # Generate payment link based on gateway
        payment_link = self.generate_payment_link(gateway, transaction)
        
        return {
            "success": True,
            "payment_id": transaction.id,
            "gateway": gateway.value,
            "payment_link": payment_link,
            "amount": amount,
            "currency": currency,
            "fee": fee,
            "net_amount": net_amount,
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
        }
    
    def select_best_gateway(self, currency: str, customer_email: str) -> Optional[PaymentGateway]:
        """Select best payment gateway based on currency and customer location"""
        country = self.get_country_from_email(customer_email)
        
        for gateway, config in self.gateways.items():
            if not config.enabled:
                continue
            
            if currency in config.supported_currencies and country in config.supported_countries:
                # Select gateway with lowest fees
                if gateway == PaymentGateway.CRYPTO and currency in ["USDT", "BTC", "ETH"]:
                    return gateway
                elif gateway == PaymentGateway.MIDTRANS and currency == "IDR":
                    return gateway
                elif gateway == PaymentGateway.WISE and currency in ["USD", "EUR", "GBP", "SGD", "AUD"]:
                    return gateway
                elif gateway == PaymentGateway.STRIPE and currency in ["USD", "EUR", "GBP"]:
                    return gateway
        
        # Fallback to Stripe for USD/EUR/GBP
        if currency in ["USD", "EUR", "GBP"] and PaymentGateway.STRIPE in self.gateways:
            return PaymentGateway.STRIPE
        
        return None
    
    def calculate_fee(self, gateway: PaymentGateway, amount: float) -> float:
        """Calculate transaction fee"""
        if gateway not in self.fee_structures:
            return 0.0
        
        fee_config = self.fee_structures[gateway]
        percentage_fee = amount * fee_config["percentage"]
        fixed_fee = fee_config["fixed"]
        
        return round(percentage_fee + fixed_fee, 2)
    
    def generate_payment_link(self, gateway: PaymentGateway, transaction: Transaction) -> str:
        """Generate payment link for specific gateway"""
        base_url = "https://mahalaksmi.web.id"
        
        if gateway == PaymentGateway.STRIPE:
            return f"{base_url}/pay/stripe/{transaction.id}"
        elif gateway == PaymentGateway.PAYPAL:
            return f"{base_url}/pay/paypal/{transaction.id}"
        elif gateway == PaymentGateway.WISE:
            return f"{base_url}/pay/wise/{transaction.id}"
        elif gateway == PaymentGateway.CRYPTO:
            return f"{base_url}/pay/crypto/{transaction.id}"
        elif gateway == PaymentGateway.MIDTRANS:
            return f"{base_url}/pay/midtrans/{transaction.id}"
        
        return f"{base_url}/pay/{transaction.id}"
    
    def process_webhook(self, gateway: PaymentGateway, payload: Dict) -> Dict:
        """Process payment webhook from gateway"""
        try:
            transaction_id = payload.get("transaction_id") or payload.get("id")
            status = payload.get("status", "pending")
            amount = payload.get("amount", 0.0)
            
            # Update transaction in database
            if status == "completed" or status == "success":
                self.db.update_transaction_status(
                    transaction_id, 
                    "completed", 
                    datetime.now().isoformat()
                )
                
                # Trigger payout if enabled
                if self.gateways[gateway].auto_payout:
                    # Get transaction from DB
                    conn = self.db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
                    row = cursor.fetchone()
                    conn.close()
                    
                    if row:
                        txn_data = dict(row)
                        payout = Payout(
                            id=f"PAYOUT-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                            amount=txn_data["net_amount"],
                            currency=txn_data["currency"],
                            destination=self.ceo_bank_account["account"] if txn_data["currency"] == "IDR" else self.ceo_crypto_wallet["address"],
                            destination_type="bank" if txn_data["currency"] == "IDR" else "crypto",
                            status="processing",
                            reference=transaction_id
                        )
                        self.db.insert_payout(payout)
                
                # Send notification
                self.send_payment_notification_from_db(transaction_id)
                
                return {"success": True, "status": "completed", "transaction_id": transaction_id}
            
            elif status == "failed":
                self.db.update_transaction_status(transaction_id, "failed")
                return {"success": False, "status": "failed", "error": payload.get("error")}
            
            return {"success": True, "status": "pending"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ========== PAYOUT MANAGEMENT ==========
    def trigger_payout(self, transaction: Transaction):
        """Trigger automatic payout to CEO"""
        try:
            # Determine payout destination based on currency
            if transaction.currency == "IDR":
                destination = self.ceo_bank_account["account"]
                destination_type = "bank"
            elif transaction.currency in ["USDT", "BTC", "ETH"]:
                destination = self.ceo_crypto_wallet["address"]
                destination_type = "crypto"
            else:
                # Convert to IDR and send to bank
                destination = self.ceo_bank_account["account"]
                destination_type = "bank"
            
            # Create payout record
            payout = Payout(
                id=f"PAYOUT-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                amount=transaction.net_amount,
                currency=transaction.currency,
                destination=destination,
                destination_type=destination_type,
                status="processing",
                fee_amount=0.0,
                net_amount=transaction.net_amount,
                reference=transaction.id
            )
            
            self.payouts.append(payout)
            
            # Execute payout
            self.execute_payout(payout)
            
        except Exception as e:
            print(f"PAYOUT ERROR: {str(e)}")
    
    def execute_payout(self, payout: Payout):
        """Execute payout to CEO"""
        try:
            # In production: integrate with actual payout APIs
            # For now, log the payout
            
            payout.status = "completed"
            payout.completed_at = datetime.now()
            
            print(f"💰 PAYOUT EXECUTED: {payout.id}")
            print(f"   Amount: {payout.amount} {payout.currency}")
            print(f"   Destination: {payout.destination}")
            print(f"   Type: {payout.destination_type}")
            print(f"   Status: {payout.status}")
            
        except Exception as e:
            payout.status = "failed"
            print(f"PAYOUT FAILED: {payout.id} - {str(e)}")
    
    def daily_payout_cycle(self):
        """Execute daily payout cycle at 23:59"""
        revenue_stats = self.db.get_revenue_stats()
        today = datetime.now().strftime("%Y-%m-%d")
        total = revenue_stats["today_revenue"]
        
        if total > 0:
            print(f"💰 DAILY PAYOUT CYCLE: {today}")
            print(f"   Total Revenue: ${total:,.2f}")
            print(f"   CEO Share (80%): ${total * 0.8:,.2f}")
            print(f"   Ops Share (20%): ${total * 0.2:,.2f}")
            
            # Create daily payout in database
            payout = Payout(
                id=f"PAYOUT-DAILY-{datetime.now().strftime('%Y%m%d')}",
                amount=total * 0.8,
                currency="USD",
                destination=self.ceo_bank_account["account"],
                destination_type="bank",
                status="processing",
                net_amount=total * 0.8
            )
            
            self.db.insert_payout(payout)
            print(f"   Payout created: {payout.id}")
            print(f"   Destination: BCA 6485086645")
            print(f"   Status: {payout.status}")
    
    # ========== REPORTING ==========
    def update_totals(self, transaction: Transaction):
        """Update daily and monthly totals"""
        today = transaction.completed_at.strftime("%Y-%m-%d") if transaction.completed_at else datetime.now().strftime("%Y-%m-%d")
        month = transaction.completed_at.strftime("%Y-%m") if transaction.completed_at else datetime.now().strftime("%Y-%m")
        
        # Daily totals
        if today not in self.daily_totals:
            self.daily_totals[today] = 0.0
        self.daily_totals[today] += transaction.net_amount
        
        # Monthly totals
        if month not in self.monthly_totals:
            self.monthly_totals[month] = 0.0
        self.monthly_totals[month] += transaction.net_amount
    
    def generate_daily_financial_report(self) -> Dict:
        """Generate daily financial report for CEO"""
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        today_revenue = self.daily_totals.get(today, 0.0)
        yesterday_revenue = self.daily_totals.get(yesterday, 0.0)
        
        # Calculate change
        if yesterday_revenue > 0:
            change_pct = ((today_revenue - yesterday_revenue) / yesterday_revenue) * 100
        else:
            change_pct = 0.0
        
        report = {
            "date": today,
            "timestamp": datetime.now().isoformat(),
            "revenue": {
                "today_usd": today_revenue,
                "yesterday_usd": yesterday_revenue,
                "change_pct": round(change_pct, 1),
                "target_usd": 500.0,
                "target_met": today_revenue >= 500.0
            },
            "ceo_share": {
                "amount_usd": today_revenue * 0.8,
                "amount_idr": today_revenue * 0.8 * self.fx_rates["USD_IDR"],
                "destination": "BCA 6485086645",
                "status": "scheduled_23:59"
            },
            "transactions": {
                "total": len([t for t in self.transactions if t.created_at.strftime("%Y-%m-%d") == today]),
                "completed": len([t for t in self.transactions if t.status == "completed" and t.created_at.strftime("%Y-%m-%d") == today]),
                "pending": len([t for t in self.transactions if t.status == "pending" and t.created_at.strftime("%Y-%m-%d") == today]),
                "failed": len([t for t in self.transactions if t.status == "failed" and t.created_at.strftime("%Y-%m-%d") == today])
            },
            "payouts": {
                "today_count": len([p for p in self.payouts if p.created_at.strftime("%Y-%m-%d") == today]),
                "today_amount": sum([p.amount for p in self.payouts if p.created_at.strftime("%Y-%m-%d") == today]),
                "pending": len([p for p in self.payouts if p.status == "pending"]),
                "completed": len([p for p in self.payouts if p.status == "completed"])
            },
            "gateway_breakdown": self._get_gateway_breakdown(today)
        }
        
        return report
    
    def _get_gateway_breakdown(self, date: str) -> Dict:
        """Get breakdown by payment gateway"""
        breakdown = {}
        
        for gateway in PaymentGateway:
            txns = [t for t in self.transactions if t.gateway == gateway and t.created_at.strftime("%Y-%m-%d") == date]
            if txns:
                breakdown[gateway.value] = {
                    "count": len(txns),
                    "total_amount": sum(t.amount for t in txns),
                    "total_fees": sum(t.fee_amount for t in txns),
                    "net_amount": sum(t.net_amount for t in txns)
                }
        
        return breakdown
    
    def send_ceo_financial_report(self, report: Dict):
        """Send financial report to CEO"""
        message = f"""
📊 DAILY FINANCIAL REPORT - {report['date']}
═══════════════════════════════════════

💰 REVENUE:
• Today: ${report['revenue']['today_usd']:,.2f}
• Yesterday: ${report['revenue']['yesterday_usd']:,.2f}
• Change: {report['revenue']['change_pct']:+.1f}%
• Target: ${report['revenue']['target_usd']:,.2f}
• Status: {'✅ TARGET MET' if report['revenue']['target_met'] else '🎯 IN PROGRESS'}

👑 CEO SHARE (80%):
• Amount: ${report['ceo_share']['amount_usd']:,.2f}
• IDR: Rp {report['ceo_share']['amount_idr']:,.0f}
• Destination: {report['ceo_share']['destination']}
• Transfer: {report['ceo_share']['status']}

📊 TRANSACTIONS:
• Total: {report['transactions']['total']}
• Completed: {report['transactions']['completed']}
• Pending: {report['transactions']['pending']}
• Failed: {report['transactions']['failed']}

💸 PAYOUTS:
• Today: {report['payouts']['today_count']} payouts
• Amount: ${report['payouts']['today_amount']:,.2f}
• Pending: {report['payouts']['pending']}
• Completed: {report['payouts']['completed']}

📈 GATEWAY BREAKDOWN:
"""
        
        for gateway, data in report["gateway_breakdown"].items():
            message += f"• {gateway}: {data['count']} txns, ${data['total_amount']:,.2f}\n"
        
        message += """
═══════════════════════════════════════
🤖 Autonomous Finance Agent
💰 All payment operations automated
🌐 mahalaksmi.web.id
        """
        
        # Send to CEO
        self.send_report_to_ceo(message, report)
    
    def send_report_to_ceo(self, message: str, report: Dict):
        """Send report to CEO via WhatsApp and Email"""
        # In production: integrate with WhatsApp Business API and SMTP
        print(f"\n📱 CEO REPORT SENT:")
        print(message)
        
        # Save report
        self.save_report(report)
    
    def save_report(self, report: Dict):
        """Save report to file"""
        filename = f"autonomous-sales-agent/logs/finance-{report['date']}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
    
    # ========== UTILITIES ==========
    def get_country_from_email(self, email: str) -> str:
        """Extract country from email domain"""
        domain = email.split("@")[-1].lower()
        
        country_map = {
            "id": "ID",
            "us": "US",
            "uk": "UK",
            "au": "AU",
            "sg": "SG",
            "de": "DE",
            "fr": "FR",
            "es": "ES",
            "br": "BR",
            "mx": "MX",
            "ar": "AR",
            "co": "CO",
            "cl": "CL",
            "jp": "JP",
            "cn": "CN",
            "tw": "TW",
            "hk": "HK",
            "kr": "KR",
            "in": "IN",
            "vn": "VN",
            "th": "TH",
            "my": "MY",
            "ph": "PH",
            "ae": "AE",
            "sa": "SA",
            "eg": "EG",
            "qa": "QA",
            "kw": "KW",
            "global": "global"
        }
        
        return country_map.get(domain, "US")
    
    def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> float:
        """Convert currency using FX rates"""
        if from_currency == to_currency:
            return amount
        
        # Convert to USD first
        if from_currency != "USD":
            usd_amount = amount / self.fx_rates.get(f"USD_{from_currency}", 1.0)
        else:
            usd_amount = amount
        
        # Convert to target currency
        if to_currency != "USD":
            return usd_amount * self.fx_rates.get(f"USD_{to_currency}", 1.0)
        
        return usd_amount
    
    def send_payment_notification(self, transaction: Transaction):
        """Send payment notification to customer"""
        message = f"""
✅ PAYMENT CONFIRMED

Dear {transaction.customer_name},

Your payment has been confirmed!

Transaction ID: {transaction.id}
Amount: {transaction.amount} {transaction.currency}
Product: {transaction.product_id}

Your order is being processed.
Estimated delivery: 24 hours

Thank you for your purchase!
MAHA LAKSHMI HOLDINGS
        """
        
        # In production: send via email/WhatsApp
        print(f"\n📧 PAYMENT NOTIFICATION to {transaction.customer_email}:")
        print(message)
    
    def send_payment_notification_from_db(self, transaction_id: str):
        """Send payment notification using database data"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            txn = dict(row)
            message = f"""
✅ PAYMENT CONFIRMED

Dear {txn['customer_name']},

Your payment has been confirmed!

Transaction ID: {txn['id']}
Amount: {txn['amount']} {txn['currency']}
Product: {txn['product_id']}

Your order is being processed.
Estimated delivery: 24 hours

Thank you for your purchase!
MAHA LAKSHMI HOLDINGS
            """
            print(f"\n📧 PAYMENT NOTIFICATION to {txn['customer_email']}:")
            print(message)
    
    def get_financial_summary(self) -> Dict:
        """Get financial summary from database"""
        return self.db.get_revenue_stats()
    
    def run_daily_cycle(self):
        """Run daily finance cycle"""
        print("=" * 70)
        print("💰 AUTONOMOUS FINANCE AGENT - DAILY CYCLE")
        print("=" * 70)
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. Process pending transactions
        self.process_pending_transactions()
        
        # 2. Reconcile transactions
        self.reconcile_transactions()
        
        # 3. Execute daily payout at 23:59
        now = datetime.now()
        if now.strftime("%H:%M") >= "23:59":
            self.daily_payout_cycle()
        
        # 4. Generate daily report
        report = self.generate_daily_financial_report()
        self.send_ceo_financial_report(report)
        
        print("=" * 70)
        print("✅ Daily finance cycle completed")
        print("=" * 70)
    
    def process_pending_transactions(self):
        """Process all pending transactions"""
        pending = [t for t in self.transactions if t.status == "pending"]
        
        for txn in pending:
            # In production: check actual payment status via API
            # For now, simulate completion
            if random.random() < 0.3:  # 30% chance of completion
                txn.status = "completed"
                txn.completed_at = datetime.now()
                self.update_totals(txn)
                print(f"✅ Transaction completed: {txn.id}")
    
    def reconcile_transactions(self):
        """Reconcile all transactions"""
        completed = [t for t in self.transactions if t.status == "completed"]
        total = sum(t.net_amount for t in completed)
        
        print(f"📊 Reconciliation: {len(completed)} transactions, ${total:,.2f} total")


# ============== MAIN ==============
def main():
    """Main entry point"""
    agent = AutonomousFinanceAgent()
    
    print("=" * 70)
    print("💰 AUTONOMOUS FINANCE AGENT")
    print("=" * 70)
    print("Payment Gateways: Stripe, PayPal, Wise, Crypto, Midtrans")
    print("Auto-payout to CEO: BCA 6485086645 / USDT TRC20")
    print("=" * 70)
    
    # Run daily cycle
    agent.run_daily_cycle()


if __name__ == "__main__":
    main()
