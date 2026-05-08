from sqlalchemy.orm import Session
from app.models.users import User
from app.models.password_reset import PasswordReset
from fastapi import HTTPException
from datetime import timedelta, datetime
from app.services.email_service import _send_email_base
import secrets
import random

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

def forgot_password_logic(db: Session, email: str) -> dict:
    user = get_user_by_email(db, email)
    if not user:
        return {"success": False, "email_exists": False}

    otp_code = str(random.randint(1000, 9999))
    expires = datetime.utcnow() + timedelta(hours=1)

    db.query(PasswordReset).filter(PasswordReset.email == email).delete()

    reset_request = PasswordReset(email=email, token=otp_code, expires=expires)
    db.add(reset_request)
    db.commit()

    html = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 500px; margin: 0 auto; border: 1px solid #e1e1e1; border-radius: 10px; overflow: hidden;">
                <div style="background-color: #1493F7; padding: 20px; text-align: center;">
                    <h1 style="color: white; margin: 0;">TutoratUp</h1>
                </div>
                <div style="padding: 30px;">
                    <h2 style="color: #333;">Reset Your Password</h2>
                    <p>You have requested to reset your password for your TutoratUp account.</p>
                    <p>Here is your 4-digit verification code:</p>
                    <div style="background-color: #f8f9fa; padding: 20px; text-align: center; border-radius: 8px; margin: 20px 0;">
                        <h1 style="color: #1493F7; letter-spacing: 4px; margin: 0;">{otp_code}</h1>
                    </div>
                    <p style="color: #666;">This code will expire in 1 hour.</p>
                    <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                    <p style="text-align: center; color: #999; font-size: 12px;">If you did not request this, please ignore this email.</p>
                </div>
            </div>
        </body>
    </html>
    """

    success, message = _send_email_base(email, "Reset Password Code - TutoratUp", html)

    if not success:
        print(f"[FORGOT PASSWORD] Email failed: {message}. OTP for {email}: {otp_code}")

    return {"success": True, "email_exists": True, "email_sent": success}

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


