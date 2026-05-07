from fastapi import APIRouter, Depends, HTTPException, FastAPI, UploadFile, File

from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.users import User
from app.models.teacher import Teacher
from app.crud.crud_teacher import create_teacher, get_teacher, get_teachers, delete_teacher, delete_all_teachers, modify_password, modify_profile, update_payment_method, get_top_rated_teachers
from typing import List
from app.schemas.teacher import TeacherCreate, TeacherOut
import os
from uuid import uuid4

router = APIRouter(
    prefix="/teachers",
    tags=["teachers"],
)

PROFILE_UPLOAD_DIR = "uploads/profiles"
os.makedirs(PROFILE_UPLOAD_DIR, exist_ok=True)

CERT_UPLOAD_DIR = "uploads/certificates"
os.makedirs(CERT_UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=TeacherOut)
def create_teacher_endpoint(teacher: TeacherCreate, db: Session = Depends(get_db)):
  return create_teacher(db, teacher)

@router.get("/top-rated", response_model=List[TeacherOut])
def get_top_rated_teachers_endpoint(limit: int = 3, db: Session = Depends(get_db)):
  return get_top_rated_teachers(db, limit)

@router.get("/{teacher_id}", response_model=TeacherOut)
def get_teacher_endpoint(teacher_id: int, db: Session = Depends(get_db)):
  teacher = get_teacher(db, teacher_id)
  if not teacher:
    raise HTTPException(status_code=404, detail="Teacher not found")
  return teacher

@router.delete("/{teacher_email}")
def delete_teacher_endpoint(teacher_email: str, teacher_password: str, db: Session = Depends(get_db)):
  if delete_teacher(db, teacher_email, teacher_password):
    return {"message": "Teacher deleted successfully"}
  raise HTTPException(status_code=404, detail="Teacher not found")

@router.get("/", response_model=List[TeacherOut])
def get_teachers_endpoint(db: Session = Depends(get_db)):
  return get_teachers(db)

@router.delete("/")
def delete_all_teachers_endpoint(db: Session = Depends(get_db)):
  delete_all_teachers(db)
  return {"message": "All teachers deleted successfully"}

@router.put("/modify_password")
def modify_password_endpoint(
  old_password: str,
  new_password: str,
  email: str | None = None,
  teacher_username: str | None = None,
  db: Session = Depends(get_db)
):
  identifier = (email or teacher_username or "").strip()
  if not identifier:
    raise HTTPException(status_code=400, detail="email is required")
  return modify_password(db, identifier, old_password, new_password)

@router.put("/modify_profile")
def modify_profile_endpoint(bio: str, domain: str, subject: str, teachinglevel: str, education_mode: str, postal_address: str, email: str, db: Session = Depends(get_db)):
  return modify_profile(db, bio, domain, subject, teachinglevel, education_mode, postal_address, email)

@router.put("/change_personal_info")
def change_personal_info_endpoint(
  bio: str,
  domain: str,
  subject: str,
  teachinglevel: str,
  education_mode: str,
  postal_address: str,
  email: str,
  profile_picture: str | None = None,
  db: Session = Depends(get_db)
):
  return modify_profile(db, bio, domain, subject, teachinglevel, education_mode, postal_address, email, profile_picture)

@router.delete("/delete_profile/{teacher_email}")
def delete_profile_endpoint(teacher_email: str, teacher_password: str, db: Session = Depends(get_db)):
  if delete_teacher(db, teacher_email, teacher_password):
    return {"message": "Teacher profile deleted successfully"}
  raise HTTPException(status_code=404, detail="Teacher not found")
@router.put("/update_payment_method")
def update_payment_method_endpoint(email: str, payment_method: str, payment_info: str, db: Session = Depends(get_db)):
  return update_payment_method(db, email, payment_method, payment_info)

import base64

@router.post("/upload-profile-picture")
async def upload_profile_picture(file: UploadFile = File(...)):
  content_type = (file.content_type or "image/jpeg").lower()
  if not content_type.startswith("image/"):
    raise HTTPException(status_code=400, detail="Only image files are allowed")

  data = await file.read()
  b64_encoded = base64.b64encode(data).decode('utf-8')
  base64_string = f"data:{content_type};base64,{b64_encoded}"

  return {"profile_picture": base64_string}


@router.post("/upload-certificate")
async def upload_certificate(file: UploadFile = File(...)):
  content_type = (file.content_type or "").lower()
  is_image = content_type.startswith("image/")
  is_pdf = content_type == "application/pdf"
  if not (is_image or is_pdf):
    raise HTTPException(status_code=400, detail="Only image or PDF files are allowed")

  original_name = file.filename or "certificate"
  _, ext = os.path.splitext(original_name)
  ext = (ext or "").lower()
  if not ext:
    ext = ".pdf" if is_pdf else ".jpg"

  filename = f"{uuid4().hex}{ext}"
  file_path = os.path.join(CERT_UPLOAD_DIR, filename)

  with open(file_path, "wb") as out_file:
    out_file.write(await file.read())

  normalized = file_path.replace("\\", "/")
  if not normalized.startswith("/"):
    normalized = f"/{normalized}"

  return {
    "file_path": normalized,
    "title": original_name,
  }
