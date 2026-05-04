import os
import random
import string
import smtplib
import logging
import ssl
from typing import Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings

# ============ Configuration ============
SMTP_SERVER = os.getenv("SMTP_SERVER", settings.smtp_server)
SMTP_PORT = int(os.getenv("SMTP_PORT", str(settings.smtp_port)))
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", settings.email_address).strip()
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", settings.email_password).strip()
SENDER_NAME = os.getenv("SENDER_NAME", settings.sender_name)
ENABLE_EMAIL_DEBUG = os.getenv(
    "ENABLE_EMAIL_DEBUG",
    str(settings.enable_email_debug),
).lower() == "true"
MAX_EMAIL_RETRIES = int(os.getenv("MAX_EMAIL_RETRIES", str(settings.max_email_retries)))

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def generate_otp(length: int = 4) -> str:
    """Generate OTP code of specified length (digits only)"""
    return "".join(random.choices(string.digits, k=length))

def test_smtp_connection() -> Tuple[bool, str]:
    """Test SMTP connection to validate credentials"""
    logger.info(f"Testing SMTP connection to {SMTP_SERVER}:{SMTP_PORT}")
    logger.info(f"Using email: {EMAIL_ADDRESS}")
    
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        error_msg = "EMAIL_ADDRESS or EMAIL_PASSWORD not configured. Email sending disabled."
        logger.warning(error_msg)
        return False, error_msg
    
    try:
        if ENABLE_EMAIL_DEBUG and str(SMTP_SERVER) in ["smtp.gmail.com"]:
            logger.info("Email debug is True. Skipping real SMTP connection test to avoid timeouts.")
            return True, "SMTP connection skipped (debug mode)"

        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        if SMTP_PORT == 465:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=5, context=context) as server:
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        else:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=5) as server:
                server.starttls(context=context)
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        logger.info("SMTP connection test SUCCESSFUL")
        return True, "SMTP connection successful"
    except Exception as e:
        error_msg = f"Unexpected error testing SMTP: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

def _send_email_base(email: str, subject: str, body_html: str) -> Tuple[bool, str]:
    """Base internal helper for sending emails with retries"""
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        if ENABLE_EMAIL_DEBUG:
            logger.warning(
                "EMAIL_ADDRESS or EMAIL_PASSWORD not configured. DEBUG MODE: Logged email to %s with subject %s",
                email, subject
            )
            return True, "Email debug mode active."
        return False, "Email credentials not configured."

    for attempt in range(1, MAX_EMAIL_RETRIES + 1):
        try:
            msg = MIMEMultipart()
            msg["From"] = f"{SENDER_NAME} <{EMAIL_ADDRESS}>"
            msg["To"] = email
            msg["Subject"] = subject
            msg.attach(MIMEText(body_html, "html"))

            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            if SMTP_PORT == 465:
                with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=30, context=context) as server:
                    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
                    server.starttls(context=context)
                    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                    server.send_message(msg)
            
            return True, "Email sent successfully"
        except Exception as e:
            logger.error(f"Attempt {attempt} failed: {str(e)}")
    return False, "Email failed after retries"

def send_email_otp(email: str, otp_code: str) -> Tuple[bool, str]:
    """Send OTP to email address"""
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 500px; margin: 0 auto;">
                <h2 style="color: #1FA4FF;">TutoratUp Verification</h2>
                <p>Your verification code is:</p>
                <div style="background-color: #f8f9fa; padding: 20px; text-align: center; border-radius: 8px; margin: 20px 0;">
                    <h1 style="color: #1FA4FF; letter-spacing: 2px; margin: 0;">{otp_code}</h1>
                </div>
                <p style="color: #666;">This code expires in 10 minutes.</p>
                <hr style="border: none; border-top: 1px solid #eee;">
                <p style="text-align: center; color: #999; font-size: 12px;">(c) TutoratUp - Educational Platform</p>
            </div>
        </body>
    </html>
    """
    return _send_email_base(email, "Your TutoratUp Verification Code", body)

def send_teacher_approval_email(email: str, name: str) -> Tuple[bool, str]:
    """Send approval confirmation to teacher"""
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; border: 1px solid #e1e1e1; border-radius: 10px; overflow: hidden;">
                <div style="background-color: #4CAF50; padding: 20px; text-align: center;">
                    <h1 style="color: white; margin: 0;">Welcome to TutoratUp!</h1>
                </div>
                <div style="padding: 30px;">
                    <p>Dear {name},</p>
                    <p>We are delighted to inform you that your teacher application has been <strong>approved</strong>!</p>
                    <p>You can now log in to your account and start offering your services to students.</p>
                    <p>Best regards,<br>The TutoratUp Team</p>
                </div>
            </div>
        </body>
    </html>
    """
    return _send_email_base(email, "TutoratUp: Your Application was Approved!", body)

def send_teacher_rejection_email(email: str, name: str, reason: str = None) -> Tuple[bool, str]:
    """Send rejection notification to teacher"""
    reason_html = f"<p><strong>Reason:</strong> {reason}</p>" if reason else ""
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; border: 1px solid #e1e1e1; border-radius: 10px; overflow: hidden;">
                <div style="background-color: #f44336; padding: 20px; text-align: center;">
                    <h1 style="color: white; margin: 0;">Application Status</h1>
                </div>
                <div style="padding: 30px;">
                    <p>Dear {name},</p>
                    <p>After careful review, we regret to inform you that your teacher application has been <strong>declined</strong> at this time.</p>
                    {reason_html}
                    <p>Best regards,<br>The TutoratUp Team</p>
                </div>
            </div>
        </body>
    </html>
    """
    return _send_email_base(email, "TutoratUp: Application Update", body)

def send_verification_email(email: str, otp_code: str) -> Tuple[bool, str]:
    return send_email_otp(email, otp_code)

def log_email_status():
    logger.info("EMAIL SERVICE READY")