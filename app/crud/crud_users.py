from sqlalchemy.orm import Session
from app.models.users import User
from app.models.password_reset import PasswordReset
from fastapi import HTTPException
from datetime import timedelta, datetime
import secrets

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
    import random
    user = get_user_by_email(db, email)
    if not user:
        return {"success": False, "email_exists": False}

    otp_code = str(random.randint(1000, 9999))
    expires = datetime.utcnow() + timedelta(hours=1)

    db.query(PasswordReset).filter(PasswordReset.email == email).delete()

    reset_request = PasswordReset(email=email, token=otp_code, expires=expires)
    db.add(reset_request)
    db.commit()

    return {"success": True, "email_exists": True, "otp_code": otp_code}

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


