from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.email_verification import EmailVerification
from app.models.users import User
from app.services.email_service import generate_otp, send_verification_email
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

MAX_OTP_ATTEMPTS = 3
OTP_EXPIRY_MINUTES = 10

def request_email_verification(db: Session, email: str, user_id: int = None) -> dict:
    """Request OTP verification for email"""
    logger.info(f"📧 Requesting OTP verification for email: {email}")
    
    if not email or "@" not in email:
        logger.warning(f"❌ Invalid email format: {email}")
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    existing = db.query(EmailVerification).filter(
        EmailVerification.email == email,
        EmailVerification.is_verified == True
    ).first()
    
    if existing and existing.user_id != user_id:
        logger.warning(f"❌ Email already registered: {email}")
        raise HTTPException(status_code=400, detail="Email is already registered")
    
    # Generate OTP
    otp_code = generate_otp()
    logger.info(f"✓ Generated OTP: {otp_code} for email: {email}")
    
    # Delete old unverified requests
    db.query(EmailVerification).filter(
        EmailVerification.email == email,
        EmailVerification.is_verified == False
    ).delete()
    
    # Create new verification request
    verification = EmailVerification(
        email=email,
        otp_code=otp_code,
        user_id=user_id,
        expires_at=datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)
    )
    
    db.add(verification)
    db.commit()
    logger.info(f"✓ Verification record saved to database for {email}")
    
    # Send email
    logger.info(f"📤 Sending OTP email to {email}...")
    success, message = send_verification_email(email, otp_code)
    
    if not success:
        logger.error(f"❌ Failed to send OTP email to {email}: {message}")
        status_code = 503 if "not configured" in message.lower() else 500
        raise HTTPException(status_code=status_code, detail=f"Failed to send email: {message}")
    
    logger.info(f"✅ OTP verification request successful for {email}")
    return {
        "success": True,
        "message": f"✅ OTP sent to {email}",
        "email": email,
        "expires_in_minutes": OTP_EXPIRY_MINUTES,
        "otp_debug": otp_code if logger.isEnabledFor(logging.DEBUG) else None
    }

def verify_email_otp(db: Session, email: str, otp_code: str, user_id: int = None) -> dict:
  
    
    verification = db.query(EmailVerification).filter(
        EmailVerification.email == email,
        EmailVerification.is_verified == False
    ).first()
    
    if not verification:
        raise HTTPException(status_code=400, detail="No verification request found for this email")
    
    if datetime.utcnow() > verification.expires_at:
        db.delete(verification)
        db.commit()
        raise HTTPException(status_code=400, detail="OTP has expired. Please request a new one.")
    
    if verification.attempts >= MAX_OTP_ATTEMPTS:
        db.delete(verification)
        db.commit()
        raise HTTPException(status_code=400, detail="Maximum attempts exceeded. Please request a new OTP.")
    
    if verification.otp_code != otp_code:
        verification.attempts += 1
        db.commit()
        remaining_attempts = MAX_OTP_ATTEMPTS - verification.attempts
        raise HTTPException(
            status_code=400,
            detail=f"Invalid OTP. Attempts remaining: {remaining_attempts}"
        )
    
    verification.is_verified = True
    verification.verified_at = datetime.utcnow()
    db.commit()
    
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.phone_verified = True
            db.commit()
    
    return {
        "success": True,
        "message": "Email verified successfully",
        "email": email
    }

def resend_email_otp(db: Session, email: str) -> dict:
    """Resend OTP to email"""
    logger.info(f"📧 Resending OTP for email: {email}")
    
    verification = db.query(EmailVerification).filter(
        EmailVerification.email == email,
        EmailVerification.is_verified == False
    ).first()
    
    if not verification:
        logger.warning(f"❌ No verification request found for email: {email}")
        raise HTTPException(status_code=400, detail="No verification request found")
    
    if datetime.utcnow() > verification.expires_at:
        logger.info(f"⏱️ OTP expired for {email}, creating new verification request")
        db.delete(verification)
        db.commit()
        return request_email_verification(db, email, verification.user_id)
    
    # Generate new OTP
    new_otp = generate_otp()
    logger.info(f"✓ Generated new OTP: {new_otp} for email: {email}")
    
    verification.otp_code = new_otp
    verification.attempts = 0
    verification.expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)
    db.commit()
    logger.info(f"✓ Updated verification record for {email}")
    
    # Send new email
    logger.info(f"📤 Sending new OTP email to {email}...")
    success, message = send_verification_email(email, new_otp)
    
    if not success:
        logger.error(f"❌ Failed to resend OTP email to {email}: {message}")
        status_code = 503 if "not configured" in message.lower() else 500
        raise HTTPException(status_code=status_code, detail=f"Failed to send email: {message}")
    
    logger.info(f"✅ OTP resent successfully to {email}")
    return {
        "success": True,
        "message": f"✅ New OTP sent to {email}",
        "email": email,
        "expires_in_minutes": OTP_EXPIRY_MINUTES,
        "otp_debug": new_otp if logger.isEnabledFor(logging.DEBUG) else None
    }

def check_email_verified(db: Session, user_id: int) -> bool:
    
    user = db.query(User).filter(User.id == user_id).first()
    return user.phone_verified if user else False

def get_email_verification_status(db: Session, email: str) -> dict:
    
    
    verification = db.query(EmailVerification).filter(
        EmailVerification.email == email
    ).order_by(EmailVerification.created_at.desc()).first()
    
    if not verification:
        return {"verified": False, "email": email}
    
    return {
        "verified": verification.is_verified,
        "email": email,
        "verified_at": verification.verified_at,
        "expires_at": verification.expires_at if not verification.is_verified else None
    }
