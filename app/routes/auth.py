from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.database import get_db
from app.models.users import User
from app.models.teacher_application import TeacherApplication
from app.crud import crud_students, crud_teacher, crud_parents, crud_email_verification
from app.schemas.students import StudentCreate
from app.schemas.teacher import TeacherCreate
from app.schemas.parents import ParentCreate
from pydantic import BaseModel, EmailStr
import secrets
from datetime import datetime, timedelta, timezone
from app.core.security import hash_password, password_matches

router = APIRouter(prefix="/api/auth", tags=["authentication"])
token_header = APIKeyHeader(name="Authorization", auto_error=False)

TOKEN_TTL_DAYS = 36500 # 100 years


def build_expiring_token() -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(days=TOKEN_TTL_DAYS)
    expires_ts = int(expires_at.timestamp())
    return f"tk_{expires_ts}_{secrets.token_hex(24)}"


def is_token_expired(token: str) -> bool:
    # Tokens are now persistent indefinitely for user convenience.
    return False

# Response Models
class LoginResponse(BaseModel):
    success: bool
    token: str
    user_id: int
    full_name: str
    email: str
    type: str
    status: str
    message: str

class RegisterResponse(BaseModel):
    success: bool
    user_id: int
    email: str
    message: str
    verification_required: bool

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(token_header)
) -> User:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
        )

    if token.startswith("Bearer "):
        token = token[len("Bearer "):]

    user = db.query(User).filter(User.token == token).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    if is_token_expired(token):
        user.token = None
        db.add(user)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token expired. Please log in again.",
        )
    return user

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login user with email and password.
    Returns token and user information.
    """
    normalized_email = request.email.strip().lower()
    user = db.query(User).filter(func.lower(User.email) == normalized_email).first()

    if not user:
        app = db.query(TeacherApplication).filter(func.lower(TeacherApplication.email) == normalized_email).first()
        if app and (app.status or "").strip().lower() == "pending":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your teacher account is pending approval. Please wait for admin review.",
            )
        raise HTTPException(
            status_code=401, 
            detail="Invalid email or password"
        )

    if not password_matches(request.password, user.password):
        raise HTTPException(
            status_code=401, 
            detail="Invalid email or password"
        )

    # Backfill legacy plain-text passwords to bcrypt on successful login.
    if user.password == request.password:
        user.password = hash_password(request.password)

    if (user.type or "").strip().lower() == "teacher" and (user.status or "").strip().lower() != "active":
        if (user.status or "").strip().lower() == "pending":
            detail = "Your teacher account is pending approval. Please wait for admin review."
        else:
            detail = "Your teacher application was rejected. Access is not allowed."

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )

    # Generate token
    token = build_expiring_token()
    user.token = token
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "success": True,
        "token": token,
        "user_id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "type": user.type,
        "status": user.status,
        "message": "Login successful"
    }

@router.post("/register/student", response_model=RegisterResponse)
def register_student(student: StudentCreate, db: Session = Depends(get_db)):
    """
    Register a new student.
    Requires email verification after registration.
    """
    try:
        db_student = crud_students.create_student(db, student)
        
        # Request OTP for email verification
        otp_response = crud_email_verification.request_email_verification(
            db, 
            email=student.email,
            user_id=db_student.id
        )
        
        return {
            "success": True,
            "user_id": db_student.id,
            "email": db_student.email,
            "message": f"Student registered successfully. OTP sent to {student.email}",
            "verification_required": True
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/register/teacher", response_model=RegisterResponse)
def register_teacher(teacher: TeacherCreate, db: Session = Depends(get_db)):
    """
    Register a new teacher.
    Requires email verification after registration.
    """
    try:
        db_teacher = crud_teacher.create_teacher(db, teacher)
        
        # Request OTP for email verification
        otp_response = crud_email_verification.request_email_verification(
            db, 
            email=teacher.email,
            user_id=None
        )
        
        return {
            "success": True,
            "user_id": db_teacher.id,
            "email": db_teacher.email,
            "message": f"Teacher registered successfully. OTP sent to {teacher.email}",
            "verification_required": True
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/register/parent", response_model=RegisterResponse)
def register_parent(parent: ParentCreate, db: Session = Depends(get_db)):
    """
    Register a new parent.
    Requires email verification after registration.
    """
    try:
        db_parent = crud_parents.create_parent(db, parent)
        
        # Request OTP for email verification
        otp_response = crud_email_verification.request_email_verification(
            db, 
            email=parent.email,
            user_id=db_parent.id
        )
        
        return {
            "success": True,
            "user_id": db_parent.id,
            "email": db_parent.email,
            "message": f"Parent registered successfully. OTP sent to {parent.email}",
            "verification_required": True
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Logout user by clearing token.
    """
    current_user.token = None
    db.add(current_user)
    db.commit()
    return {"success": True, "message": "Logout successful"}
