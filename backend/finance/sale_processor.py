"""
MAHA LAKSHMI CORP - Sale Processor
Processes Gumroad webhook events into financial records.
End-to-end: Webhook → Transaction → Payment → Order → Revenue → Dashboard
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dataclasses import dataclass

from backend.db.connection import execute_query, get_connection

logger = logging.getLogger(__name__)


@dataclass
class SaleEvent:
    gumroad_purchase_id: str
    product_id: str
    marketplace_product_id: str
    account_id: str
    customer_email: str
    customer_name: str
    amount: float
    currency: str
    tax: float
    fee: float
    net_amount: float
    payment_method: str
    payment_status: str
    license_key: Optional[str]
    sale_date: str


class SaleProcessor:
    """Processes sales events and creates financial records"""
    
    def process_purchase(self, event: SaleEvent) -> Dict[str, Any]:
        """Process a purchase event"""
        try:
            with get_connection() as conn:
                # 1. Create marketplace_sales record
                sale_id = f"sale-{int(datetime.now().timestamp() * 1000)}"
                conn.execute(
                    """
                    INSERT INTO marketplace_sales 
                    (id, gumroad_purchase_id, product_id, marketplace_product_id, account_id,
                     customer_email, customer_name, amount, currency, tax, fee, net_amount,
                     payment_method, payment_status, license_key, sale_date, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        sale_id,
                        event.gumroad_purchase_id,
                        event.product_id,
                        event.marketplace_product_id,
                        event.account_id,
                        event.customer_email,
                        event.customer_name,
                        event.amount,
                        event.currency,
                        event.tax,
                        event.fee,
                        event.net_amount,
                        event.payment_method,
                        event.payment_status,
                        event.license_key,
                        event.sale_date,
                        datetime.now().isoformat()
                    )
                )
                
                # 2. Create transaction record
                transaction_id = f"txn-{int(datetime.now().timestamp() * 1000)}"
                conn.execute(
                    """
                    INSERT INTO transactions 
                    (id, type, category, amount, currency, description, reference_id, metadata, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        transaction_id,
                        "revenue",
                        "marketplace_sale",
                        event.net_amount,
                        event.currency,
                        f"Gumroad sale: {event.customer_email}",
                        event.gumroad_purchase_id,
                        json.dumps({
                            "sale_id": sale_id,
                            "product_id": event.product_id,
                            "marketplace_product_id": event.marketplace_product_id,
                            "account_id": event.account_id,
                            "gross_amount": event.amount,
                            "tax": event.tax,
                            "fee": event.fee,
                            "payment_method": event.payment_method,
                            "license_key": event.license_key
                        }),
                        datetime.now().isoformat()
                    )
                )
                
                # 3. Create payment record
                payment_id = f"pay-{int(datetime.now().timestamp() * 1000)}"
                conn.execute(
                    """
                    INSERT INTO payments 
                    (id, order_id, amount, currency, method, status, transaction_id, gateway, paid_at, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        payment_id,
                        None,  # order_id will be linked later if needed
                        event.net_amount,
                        event.currency,
                        event.payment_method,
                        "completed",
                        transaction_id,
                        "gumroad",
                        event.sale_date,
                        datetime.now().isoformat()
                    )
                )
                
                # 4. Create accounting entries (double-entry)
                self._create_accounting_entries(conn, event, transaction_id, sale_id)
                
                # 5. Update revenue records
                self._update_revenue_record(conn, event)
                
                conn.commit()
                
                logger.info(f"Sale processed: {sale_id} - {event.gumroad_purchase_id}")
                
                return {
                    "success": True,
                    "sale_id": sale_id,
                    "transaction_id": transaction_id,
                    "payment_id": payment_id
                }
                
        except Exception as e:
            logger.error(f"Failed to process sale: {e}")
            return {"success": False, "error": str(e)}
    
    def process_refund(self, event: SaleEvent) -> Dict[str, Any]:
        """Process a refund event"""
        try:
            with get_connection() as conn:
                # Find original sale
                sale = conn.execute(
                    "SELECT * FROM marketplace_sales WHERE gumroad_purchase_id = ?",
                    (event.gumroad_purchase_id,)
                ).fetchone()
                
                if not sale:
                    logger.warning(f"Refund for unknown sale: {event.gumroad_purchase_id}")
                    return {"success": False, "error": "Original sale not found"}
                
                # Update sale record
                conn.execute(
                    """
                    UPDATE marketplace_sales 
                    SET refunded = 1, refund_amount = ?, payment_status = 'refunded'
                    WHERE gumroad_purchase_id = ?
                    """,
                    (event.amount, event.gumroad_purchase_id)
                )
                
                # Create refund transaction
                transaction_id = f"txn-{int(datetime.now().timestamp() * 1000)}"
                conn.execute(
                    """
                    INSERT INTO transactions 
                    (id, type, category, amount, currency, description, reference_id, metadata, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        transaction_id,
                        "refund",
                        "marketplace_refund",
                        -event.amount,
                        event.currency,
                        f"Gumroad refund: {event.customer_email}",
                        event.gumroad_purchase_id,
                        json.dumps({"sale_id": sale["id"], "reason": "customer_refund"}),
                        datetime.now().isoformat()
                    )
                )
                
                # Create accounting entries for refund
                self._create_refund_accounting_entries(conn, event, transaction_id, sale["id"])
                
                # Update revenue record
                self._update_revenue_refund(conn, event)
                
                conn.commit()
                
                logger.info(f"Refund processed: {event.gumroad_purchase_id}")
                return {"success": True, "transaction_id": transaction_id}
                
        except Exception as e:
            logger.error(f"Failed to process refund: {e}")
            return {"success": False, "error": str(e)}
    
    def process_chargeback(self, event: SaleEvent) -> Dict[str, Any]:
        """Process a chargeback event"""
        try:
            with get_connection() as conn:
                sale = conn.execute(
                    "SELECT * FROM marketplace_sales WHERE gumroad_purchase_id = ?",
                    (event.gumroad_purchase_id,)
                ).fetchone()
                
                if not sale:
                    return {"success": False, "error": "Original sale not found"}
                
                conn.execute(
                    """
                    UPDATE marketplace_sales 
                    SET chargeback = 1, payment_status = 'chargeback'
                    WHERE gumroad_purchase_id = ?
                    """,
                    (event.gumroad_purchase_id,)
                )
                
                transaction_id = f"txn-{int(datetime.now().timestamp() * 1000)}"
                conn.execute(
                    """
                    INSERT INTO transactions 
                    (id, type, category, amount, currency, description, reference_id, metadata, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        transaction_id,
                        "chargeback",
                        "marketplace_chargeback",
                        -event.amount,
                        event.currency,
                        f"Gumroad chargeback: {event.customer_email}",
                        event.gumroad_purchase_id,
                        json.dumps({"sale_id": sale["id"], "risk": "high"}),
                        datetime.now().isoformat()
                    )
                )
                
                conn.commit()
                
                logger.info(f"Chargeback processed: {event.gumroad_purchase_id}")
                return {"success": True, "transaction_id": transaction_id}
                
        except Exception as e:
            logger.error(f"Failed to process chargeback: {e}")
            return {"success": False, "error": str(e)}
    
    def _create_accounting_entries(self, conn, event: SaleEvent, transaction_id: str, sale_id: str):
        """Create double-entry accounting records"""
        # Debit: Cash/Bank (asset increases)
        conn.execute(
            """
            INSERT INTO accounting_entries 
            (id, entry_date, account_code, account_name, entry_type, category, amount, currency, description, reference_type, reference_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"acc-{int(datetime.now().timestamp() * 1000)}-1",
                event.sale_date,
                "1000",  # Cash/Bank
                "Cash - Gumroad",
                "debit",
                "marketplace_revenue",
                event.net_amount,
                event.currency,
                f"Gumroad sale - {event.customer_email}",
                "transaction",
                transaction_id,
                datetime.now().isoformat()
            )
        )
        
        # Credit: Revenue (income increases)
        conn.execute(
            """
            INSERT INTO accounting_entries 
            (id, entry_date, account_code, account_name, entry_type, category, amount, currency, description, reference_type, reference_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"acc-{int(datetime.now().timestamp() * 1000)}-2",
                event.sale_date,
                "4000",  # Revenue
                "Product Sales",
                "credit",
                "marketplace_revenue",
                event.net_amount,
                event.currency,
                f"Gumroad sale - {event.customer_email}",
                "transaction",
                transaction_id,
                datetime.now().isoformat()
            )
        )
    
    def _create_refund_accounting_entries(self, conn, event: SaleEvent, transaction_id: str, sale_id: str):
        """Create accounting entries for refunds"""
        # Debit: Revenue (reduces revenue)
        conn.execute(
            """
            INSERT INTO accounting_entries 
            (id, entry_date, account_code, account_name, entry_type, category, amount, currency, description, reference_type, reference_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"acc-{int(datetime.now().timestamp() * 1000)}-1",
                event.sale_date,
                "4000",  # Revenue
                "Product Sales",
                "debit",
                "marketplace_refund",
                event.amount,
                event.currency,
                f"Gumroad refund - {event.customer_email}",
                "transaction",
                transaction_id,
                datetime.now().isoformat()
            )
        )
        
        # Credit: Cash/Bank (reduces asset)
        conn.execute(
            """
            INSERT INTO accounting_entries 
            (id, entry_date, account_code, account_name, entry_type, category, amount, currency, description, reference_type, reference_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"acc-{int(datetime.now().timestamp() * 1000)}-2",
                event.sale_date,
                "1000",  # Cash/Bank
                "Cash - Gumroad",
                "credit",
                "marketplace_refund",
                event.amount,
                event.currency,
                f"Gumroad refund - {event.customer_email}",
                "transaction",
                transaction_id,
                datetime.now().isoformat()
            )
        )
    
    def _update_revenue_record(self, conn, event: SaleEvent):
        """Update daily revenue record"""
        today = event.sale_date[:10]  # YYYY-MM-DD
        
        # Check if record exists
        existing = conn.execute(
            "SELECT * FROM revenue_records WHERE date = ? AND marketplace = ? AND product_id = ?",
            (today, "gumroad", event.product_id)
        ).fetchone()
        
        if existing:
            conn.execute(
                """
                UPDATE revenue_records 
                SET sales_count = sales_count + 1,
                    gross_amount = gross_amount + ?,
                    fee_amount = fee_amount + ?,
                    tax_amount = tax_amount + ?,
                    net_amount = net_amount + ?,
                    updated_at = ?
                WHERE date = ? AND marketplace = ? AND product_id = ?
                """,
                (
                    event.amount, event.fee, event.tax, event.net_amount,
                    datetime.now().isoformat(),
                    today, "gumroad", event.product_id
                )
            )
        else:
            record_id = f"rev-{int(datetime.now().timestamp() * 1000)}"
            conn.execute(
                """
                INSERT INTO revenue_records 
                (id, date, marketplace, product_id, product_name, category, sales_count,
                 gross_amount, fee_amount, tax_amount, net_amount, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record_id,
                    today,
                    "gumroad",
                    event.product_id,
                    "Unknown Product",  # Will be updated via sync
                    "digital",
                    1,
                    event.amount,
                    event.fee,
                    event.tax,
                    event.net_amount,
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                )
            )
    
    def _update_revenue_refund(self, conn, event: SaleEvent):
        """Update revenue record for refund"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        existing = conn.execute(
            "SELECT * FROM revenue_records WHERE date = ? AND marketplace = ? AND product_id = ?",
            (today, "gumroad", event.product_id)
        ).fetchone()
        
        if existing:
            conn.execute(
                """
                UPDATE revenue_records 
                SET refund_count = refund_count + 1,
                    refund_amount = refund_amount + ?,
                    net_amount = net_amount - ?,
                    updated_at = ?
                WHERE date = ? AND marketplace = ? AND product_id = ?
                """,
                (
                    event.amount, event.amount,
                    datetime.now().isoformat(),
                    today, "gumroad", event.product_id
                )
            )
