import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app.database.database import SessionLocal
from app.models.users import User
from app.models.password_reset import PasswordReset
from datetime import datetime, timedelta
from app.services.email_service import _send_email_base, generate_otp

def trigger():
    db = SessionLocal()
    email = "oa_abid@esi.dz"
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        print("User not found in DB.")
        db.close()
        return

    otp_code = generate_otp(4)
    expires = datetime.utcnow() + timedelta(hours=1)

    db.query(PasswordReset).filter(PasswordReset.email == email).delete()
    reset_request = PasswordReset(email=email, token=otp_code, expires=expires)
    db.add(reset_request)
    db.commit()
    
    print(f"OTP generated and inserted into DB: {otp_code}")

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

    success, msg = _send_email_base(email, "Reset Password Code - TutoratUp", html)
    print(f"Email sent: {success}, {msg}")
    db.close()

if __name__ == "__main__":
    trigger()
