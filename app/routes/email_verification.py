from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.crud import crud_email_verification
from app.schemas.phone_verification import (
    EmailVerificationRequest,
    OTPVerifyRequest,
    OTPResendRequest,
    EmailVerificationResponse,
    VerificationStatusResponse
)

router = APIRouter(prefix="/api/email-verification", tags=["email-verification"])

@router.post("/request-otp", response_model=EmailVerificationResponse)
def request_otp(request: EmailVerificationRequest, db: Session = Depends(get_db)):
    """
    Request OTP for email verification.
    
    - **email**: Email address to verify
    """
    return crud_email_verification.request_email_verification(
        db, 
        email=request.email
    )

@router.post("/verify-otp", response_model=EmailVerificationResponse)
def verify_otp(request: OTPVerifyRequest, db: Session = Depends(get_db)):
    """
    Verify email with OTP code.
    
    - **email**: Email address being verified
    - **otp_code**: 6-digit OTP code from email
    """
    return crud_email_verification.verify_email_otp(
        db,
        email=request.email,
        otp_code=request.otp_code
    )

@router.post("/resend-otp", response_model=EmailVerificationResponse)
def resend_otp(request: OTPResendRequest, db: Session = Depends(get_db)):
    """
    Resend OTP to email address.
    
    - **email**: Email address to resend OTP to
    """
    return crud_email_verification.resend_email_otp(
        db, 
        email=request.email
    )

@router.get("/status/{email}", response_model=VerificationStatusResponse)
def get_verification_status(email: str, db: Session = Depends(get_db)):
    """
    Check email verification status.
    
    - **email**: Email address to check status for
    """
    return crud_email_verification.get_email_verification_status(
        db,
        email=email
    )
