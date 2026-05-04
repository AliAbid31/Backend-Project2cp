import os
import random
import string
from typing import Tuple

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")

def generate_otp(length: int = 6) -> str:
    """Generate OTP code"""
    return ''.join(random.choices(string.digits, k=length))

def send_sms_otp(phone_number: str, otp_code: str) -> Tuple[bool, str]:
    
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        return True, f"OTP sent to {phone_number} (mock mode)"
    
    try:
        from twilio.rest import Client
        
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        message = client.messages.create(
            body=f"Your Tutoratup verification code is: {otp_code}. This code expires in 10 minutes.",
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        
        return True, f"OTP sent successfully to {phone_number}"
        
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return False, f"Failed to send OTP: {str(e)}"

def send_verification_sms(phone_number: str, otp_code: str) -> Tuple[bool, str]:
    """
    Wrapper function to send verification SMS
    """
    return send_sms_otp(phone_number, otp_code)
