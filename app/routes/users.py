from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database.database import get_db
from app.crud import crud_users
from app.schemas.users import ForgotPasswordRequest, ResetPassword
from app.routes.autth1 import get_current_user
from app.models.users import User
import secrets

router = APIRouter(prefix="/api/users", tags=["users"])

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = crud_users.authenticate_user(db, email=credentials.email, password=credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    if user.status == "pending":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is pending admin approval. Please wait for verification.",
        )
    
    if user.status == "rejected":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been rejected. Please contact support.",
        )
    
    if user.status == "banned":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been banned. Please contact support.",
        )
    
    return {
        "token": user.token,
        "email": user.email,
        "type": user.type,
        "status": user.status
    }

@router.post("/forgot-password")
def forgot_password_endpoint(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    crud_users.forgot_password_logic(db, request.email.lower().strip())
    return {"message": "If this email is registered, a reset link will be sent"}

@router.post("/reset-password/{token}")
def reset_password_endpoint(token: str, request: ResetPassword, db: Session = Depends(get_db)):
    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    success = crud_users.reset_password_logic(db, token, request.new_password)
    if success:
        return {"message": "Password reset successfully"}
    raise HTTPException(status_code=400, detail="Invalid token or user not found")

@router.post("/logout")
def logout_endpoint(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Logout the current user by clearing their token"""
    crud_users.logout_user(db, current_user)
    return {"message": "Logged out successfully"}

@router.get("/search")
def search_users(
    q: str = Query(..., min_length=1),
    type: str = Query(None),
    db: Session = Depends(get_db)
):
    """Search for users by name or email, optionally filter by type"""
    query = db.query(User)
    
    if q:
        query = query.filter(
            (User.full_name.ilike(f"%{q}%")) | (User.email.ilike(f"%{q}%"))
        )
    
    if type:
        query = query.filter(User.type == type)
        
    users = query.limit(20).all()
    
    return [
        {
            "id": u.id,
            "name": u.full_name or "Unknown",
            "email": u.email,
            "type": u.type,
            "role": u.type,
            "avatar": f"https://ui-avatars.com/api/?name={(u.full_name or 'U').replace(' ', '+')}&background=random"
        }
        for u in users
    ]

