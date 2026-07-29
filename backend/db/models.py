"""
MAHA LAKSHMI CORP - SQLAlchemy Models
PostgreSQL-compatible ORM models for core entities.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, String, Float, Integer, Boolean, DateTime, Text, ForeignKey, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    name = Column(String)
    role = Column(String, default="user")
    totp_enabled = Column(Boolean, default=False)
    webauthn_enabled = Column(Boolean, default=False)
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)

    sessions = relationship("Session", back_populates="user")
    products = relationship("Product", back_populates="creator")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    token = Column(String, nullable=False)
    expires_at = Column(String, nullable=False)
    created_at = Column(String, nullable=False)

    user = relationship("User", back_populates="sessions")


class PasswordReset(Base):
    __tablename__ = "password_resets"

    id = Column(String, primary_key=True)
    email = Column(String, nullable=False, index=True)
    token = Column(String, nullable=False, unique=True)
    expires_at = Column(String, nullable=False)
    used = Column(Integer, default=0)
    created_at = Column(String, nullable=False)


class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False, default=0)
    currency = Column(String, nullable=False, default="USD")
    category = Column(String)
    tags = Column(Text, nullable=False, default="[]")
    status = Column(String, nullable=False, default="draft")
    content = Column(Text)
    created_by = Column(String, ForeignKey("users.id"))
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)

    creator = relationship("User", back_populates="products")
    jobs = relationship("ProductGenerationJob", back_populates="product")
    publications = relationship("MarketplacePublication", back_populates="product")


class ProductGenerationJob(Base):
    __tablename__ = "product_generation_jobs"

    id = Column(String, primary_key=True)
    product_data = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="queued")
    worker_id = Column(String)
    result = Column(Text)
    error = Column(Text)
    created_by = Column(String, ForeignKey("users.id"))
    started_at = Column(String)
    completed_at = Column(String)
    attempts = Column(Integer, nullable=False, default=0)
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)

    product = relationship("Product", back_populates="jobs")


class MarketplaceAccount(Base):
    __tablename__ = "marketplace_accounts"

    id = Column(String, primary_key=True)
    provider = Column(String, nullable=False)
    name = Column(String, nullable=False)
    api_key = Column(String, nullable=False)
    status = Column(String, nullable=False, default="active")
    last_sync_at = Column(String)
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)

    products = relationship("MarketplaceProduct", back_populates="account")
    publications = relationship("MarketplacePublication", back_populates="account")


class MarketplaceProduct(Base):
    __tablename__ = "marketplace_products"

    id = Column(String, primary_key=True)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    account_id = Column(String, ForeignKey("marketplace_accounts.id"), nullable=False)
    marketplace_product_id = Column(String)
    marketplace_url = Column(String)
    status = Column(String, nullable=False, default="draft")
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)

    product = relationship("Product")
    account = relationship("MarketplaceAccount", back_populates="products")


class MarketplacePublication(Base):
    __tablename__ = "marketplace_publications"

    id = Column(String, primary_key=True)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    account_id = Column(String, ForeignKey("marketplace_accounts.id"), nullable=False)
    provider = Column(String, nullable=False)
    status = Column(String, nullable=False)
    marketplace_product_id = Column(String)
    marketplace_url = Column(String)
    response_data = Column(Text)
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)

    product = relationship("Product", back_populates="publications")
    account = relationship("MarketplaceAccount", back_populates="publications")


class MarketplaceSale(Base):
    __tablename__ = "marketplace_sales"

    id = Column(String, primary_key=True)
    gumroad_purchase_id = Column(String, unique=True, nullable=False, index=True)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    account_id = Column(String, ForeignKey("marketplace_accounts.id"))
    marketplace_product_id = Column(String)
    customer_email = Column(String)
    customer_name = Column(String)
    amount = Column(Float, nullable=False)
    tax = Column(Float, nullable=False, default=0)
    fee = Column(Float, nullable=False, default=0)
    net_amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default="USD")
    payment_method = Column(String, default="gumroad")
    payment_status = Column(String, nullable=False)
    license_key = Column(String)
    sale_date = Column(String, nullable=False)
    created_at = Column(String, nullable=False)


class RevenueRecord(Base):
    __tablename__ = "revenue_records"

    id = Column(String, primary_key=True)
    date = Column(String, nullable=False, index=True)
    marketplace = Column(String, nullable=False)
    product_id = Column(String, ForeignKey("products.id"))
    sales_count = Column(Integer, nullable=False, default=0)
    gross_amount = Column(Float, nullable=False, default=0)
    net_amount = Column(Float, nullable=False, default=0)
    currency = Column(String, nullable=False, default="USD")
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)


class AccountingEntry(Base):
    __tablename__ = "accounting_entries"

    id = Column(String, primary_key=True)
    date = Column(String, nullable=False, index=True)
    account_code = Column(String, nullable=False)
    account_name = Column(String, nullable=False)
    entry_type = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default="USD")
    reference_id = Column(String)
    reference_type = Column(String)
    description = Column(Text)
    created_at = Column(String, nullable=False)


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True)
    sale_id = Column(String, ForeignKey("marketplace_sales.id"), nullable=False)
    payment_method = Column(String, nullable=False)
    status = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default="USD")
    marketplace = Column(String, default="gumroad")
    transaction_id = Column(String)
    created_at = Column(String, nullable=False)


class Payout(Base):
    __tablename__ = "payouts"

    id = Column(String, primary_key=True)
    marketplace = Column(String, nullable=False)
    payout_id = Column(String)
    amount = Column(Float, nullable=False)
    net_amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default="USD")
    status = Column(String, nullable=False)
    payout_date = Column(String)
    created_at = Column(String, nullable=False)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True)
    transaction_type = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default="USD")
    status = Column(String, nullable=False)
    reference_id = Column(String)
    reference_type = Column(String)
    description = Column(Text)
    created_at = Column(String, nullable=False)


class AIWorker(Base):
    __tablename__ = "ai_workers"

    id = Column(String, primary_key=True)
    worker_id = Column(String, unique=True, nullable=False, index=True)
    type = Column(String, nullable=False)
    status = Column(String, nullable=False, default="idle")
    last_heartbeat = Column(String, nullable=False)
    tasks_processed = Column(Integer, nullable=False, default=0)
    metadata = Column(Text, nullable=False, default="{}")
    created_at = Column(String, nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True)
    user_id = Column(String)
    action = Column(String, nullable=False)
    resource_type = Column(String)
    resource_id = Column(String)
    details = Column(Text)
    ip_address = Column(String)
    user_agent = Column(String)
    created_at = Column(String, nullable=False)


def get_engine(database_url: Optional[str] = None):
    """Create SQLAlchemy engine for PostgreSQL or SQLite."""
    url = database_url or "sqlite:///./data/maha_lakshmi.db"
    if url.startswith("sqlite"):
        return create_engine(url, connect_args={"check_same_thread": False})
    return create_engine(url, pool_pre_ping=True, pool_size=10, max_overflow=20)


def create_all_tables(database_url: Optional[str] = None):
    """Create all tables using SQLAlchemy."""
    engine = get_engine(database_url)
    Base.metadata.create_all(engine)
    return engine


def get_session(database_url: Optional[str] = None):
    """Create a new session factory."""
    engine = get_engine(database_url)
    Session = sessionmaker(bind=engine)
    return Session()
