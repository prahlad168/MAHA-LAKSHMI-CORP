"""
MAHA LAKSHMI CORP - Email Notification Service
SMTP-based email delivery for notifications, password resets, and alerts.
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from backend.shared.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """SMTP email service with template support."""

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        from_addr: Optional[str] = None,
    ):
        self.host = host or settings.SMTP_HOST
        self.port = port or settings.SMTP_PORT
        self.username = username or settings.SMTP_USER
        self.password = password or settings.SMTP_PASSWORD
        self.from_addr = from_addr or settings.SMTP_FROM or self.username

    def is_configured(self) -> bool:
        return bool(self.host and self.username and self.password)

    def send(
        self,
        to: str,
        subject: str,
        body: str,
        html: Optional[str] = None,
    ) -> dict:
        if not self.is_configured():
            logger.warning("SMTP not configured; email to %s suppressed", to)
            return {"success": False, "error": "SMTP not configured"}

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.from_addr
        message["To"] = to
        message.attach(MIMEText(body, "plain"))
        if html:
            message.attach(MIMEText(html, "html"))

        try:
            with smtplib.SMTP(self.host, self.port, timeout=10) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.sendmail(self.from_addr, [to], message.as_string())
            logger.info("Email sent to %s: %s", to, subject)
            return {"success": True}
        except Exception as exc:
            logger.error("Failed to send email to %s: %s", to, exc)
            return {"success": False, "error": str(exc)}


email_service = EmailService()
