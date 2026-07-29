"""
MAHA LAKSHMI CORP - Configuration and Secrets Management
Centralized configuration loader with environment variable validation.
"""

import os
import secrets
from typing import Optional


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self):
        self.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
        self.GUMROAD_API_KEY = os.getenv("GUMROAD_API_KEY")
        self.WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
        self.SMTP_HOST = os.getenv("SMTP_HOST")
        self.SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
        self.SMTP_USER = os.getenv("SMTP_USER")
        self.SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
        self.SMTP_FROM = os.getenv("SMTP_FROM", self.SMTP_USER)
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/maha_lakshmi.db")
        self.CORS_ORIGINS = os.getenv(
            "CORS_ORIGINS",
            "https://mahalaksmi.web.id,http://localhost:3000,http://localhost:8000",
        ).split(",")
        self.REDIS_URL = os.getenv("REDIS_URL")
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
