from sqlalchemy.orm import Session
from app.models.users import User
from app.models.password_reset import PasswordReset
from fastapi import HTTPException
from datetime import timedelta, datetime
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
SENDER_NAME = os.getenv("SENDER_NAME", "TutoratUp")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def get_user_by_email(db: Session, email: str) -> User:
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str) -> User:
    user = get_user_by_email(db, email)
    if not user or user.password != password:
        return None
    
    token = secrets.token_hex(32)
    user.token = token
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def forgot_password_logic(db: Session, email: str) -> bool:
    user = get_user_by_email(db, email)
    if not user:
        return False

    import random
    otp_code = str(random.randint(1000, 9999))
    expires = datetime.utcnow() + timedelta(hours=1)
    
    db.query(PasswordReset).filter(PasswordReset.email == email).delete()
    
    reset_request = PasswordReset(email=email, token=otp_code, expires=expires)
    db.add(reset_request)
    db.commit()
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Reset Password Code - TutoratUp"
    msg["From"] = f"{SENDER_NAME} <{EMAIL_ADDRESS}>"
    msg["To"] = email
    
    html = f"""
    <html>
        <body style='text-align:center; font-family: Arial, sans-serif;'>
            <h2>Reset Your Password</h2>
            <p>You have requested to reset your password for your TutoratUp account.</p>
            <p>Here is your 4-digit verification code:</p>
            <h1 style='background:#f4f4f4;color:#333;padding:12px 24px;border-radius:5px;display:inline-block;letter-spacing:4px;'>{otp_code}</h1>
            <p style='margin-top:20px; color:#666;'>This code will expire in one hour.</p>
        </body>
    </html>
    """
    msg.attach(MIMEText(html, "html"))

    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print("[FORGOT PASSWORD] SMTP credentials not configured - simulating success")
        return True

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, email, msg.as_string())
        return True
    except Exception as e:
        print(f"[FORGOT PASSWORD] SMTP Error: {e}")
        print("[FORGOT PASSWORD] SMTP failed - simulating success for security")
        return True

def verify_reset_code(db: Session, email: str, otp_code: str) -> bool:
    reset_request = db.query(PasswordReset).filter(
        PasswordReset.email == email,
        PasswordReset.token == otp_code, 
        PasswordReset.expires > datetime.utcnow()
    ).first()
    return reset_request is not None

def reset_password_logic(db: Session, email: str, otp_code: str, new_password: str) -> bool:
    reset_request = db.query(PasswordReset).filter(
        PasswordReset.email == email,
        PasswordReset.token == otp_code, 
        PasswordReset.expires > datetime.utcnow()
    ).first()
    
    if not reset_request:
        raise HTTPException(status_code=400, detail="Code invalid or expired")
    
    user = get_user_by_email(db, email)
    if user:
        from app.core.security import hash_password
        user.password = hash_password(new_password)
        db.add(user)
        db.delete(reset_request)
        db.commit()
        return True
    return False

def logout_user(db: Session, user: User) -> bool:
    user.token = None
    db.add(user)
    db.commit()
    return True


