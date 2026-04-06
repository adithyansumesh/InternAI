import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.logger import get_logger

logger = get_logger(__name__)

class EmailService:
    """Service responsible for sending emails via SMTP."""
    def __init__(self):
        self.email_user = os.environ.get("EMAIL_USER")
        self.email_pass = os.environ.get("EMAIL_PASS")
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    def send_email(self, recipient: str, subject: str, body: str) -> bool:
        if not self.email_user or not self.email_pass:
            logger.warning("EMAIL_USER or EMAIL_PASS not set. Skipping actual email sending.")
            return True # Mock success if credentials are not provided
            
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = recipient
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_pass)
                server.send_message(msg)
                
            logger.info(f"Email successfully sent to {recipient}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
