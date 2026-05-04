from fastapi import Depends, HTTPException, status, APIRouter, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.database import get_db
from app.models.users import User
from app.crud import crud_students, crud_teacher, crud_parents, crud_email_verification
from app.schemas.students import StudentCreate
from app.schemas.teacher import TeacherCreate
from app.schemas.parents import ParentCreate
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta, timezone
from app.core.security import verify_password
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from app.core.rate_limit import limiter

# --- JWT SETTINGS ---
# Tip: In production, move these to a .env file
SECRET_KEY = "your-extremely-secret-hex-code" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 14  # 14 days

router = APIRouter(prefix="/api/auth1", tags=["authentication"])

# Standard tool to extract 'Bearer <token>' from the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth1/login")

# --- SCHEMAS ---

class LoginResponse(BaseModel):
    success: bool
    token: str
    user_id: int
    full_name: str
    email: str
    type: str
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

# --- JWT UTILITIES ---

def create_access_token(data: dict):
    """Creates a signed JWT with an expiration timestamp."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- DEPENDENCY (The Gatekeeper) ---

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Stateless Gatekeeper: Decodes the token to find the user_id.
    Does NOT search for the token string in the DB.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 1. Decode the JWT using your Secret Key
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub") # 'sub' is the user_id we put in during login
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 2. Confirm the user still exists in the DB
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user

# --- AUTH ROUTES ---

@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/minute") 
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticates user and generates a signed JWT."""
    normalized_email = request.email.strip().lower()
    user = db.query(User).filter(func.lower(User.email) == normalized_email).first()

    # Compare hashed password using security utility
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(
            status_code=401, 
            detail="Invalid email or password"
        )

    # Generate the JWT (Stateless - we don't save this to the User table)
    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "success": True,
        "token": access_token,
        "user_id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "type": user.type,
        "message": "Login successful"
    }

# --- REGISTRATION ROUTES (Logic remains the same) ---

@router.post("/register/student", response_model=RegisterResponse)
@limiter.limit("3/minute")
def register_student(request, student: StudentCreate, db: Session = Depends(get_db)):
    try:
        db_student = crud_students.create_student(db, student)
        crud_email_verification.request_email_verification(db, email=student.email, user_id=db_student.id)
        return {
            "success": True, "user_id": db_student.id, "email": db_student.email,
            "message": f"Student registered successfully. OTP sent to {student.email}",
            "verification_required": True
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/register/teacher", response_model=RegisterResponse)
@limiter.limit("3/minute")
def register_teacher(request, teacher: TeacherCreate, db: Session = Depends(get_db)):
    try:
        db_teacher = crud_teacher.create_teacher(db, teacher)
        crud_email_verification.request_email_verification(db, email=teacher.email, user_id=None)
        return {
            "success": True, "user_id": db_teacher.id, "email": db_teacher.email,
            "message": f"Teacher registered successfully. OTP sent to {teacher.email}",
            "verification_required": True
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/register/parent", response_model=RegisterResponse)
@limiter.limit("3/minute")
def register_parent(request, parent: ParentCreate, db: Session = Depends(get_db)):
    try:
        db_parent = crud_parents.create_parent(db, parent)
        crud_email_verification.request_email_verification(db, email=parent.email, user_id=db_parent.id)
        return {
            "success": True, "user_id": db_parent.id, "email": db_parent.email,
            "message": f"Parent registered successfully. OTP sent to {parent.email}",
            "verification_required": True
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/logout")
def logout():
    """With JWT, the server is stateless. Logout happens by the client deleting the token."""
    return {"success": True, "message": "Logout successful (Token discarded)"}