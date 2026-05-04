from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class EmailVerificationRequest(BaseModel):
    email: str

class OTPVerifyRequest(BaseModel):
    email: str
    otp_code: str

class OTPResendRequest(BaseModel):
    email: str

class EmailVerificationResponse(BaseModel):
    success: bool
    message: str

class VerificationStatusResponse(BaseModel):
    email: Optional[str] = None
    verified: bool = False
    verified_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

PhoneVerificationRequest = EmailVerificationRequest
PhoneVerificationResponse = EmailVerificationResponse
