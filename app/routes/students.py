from fastapi import APIRouter, Depends, HTTPException,FastAPI, Query

from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.users import User
from app.models.students import Student
from app.crud.crud_students import create_student, get_student, get_students, delete_student, delete_all_students, modify_password, modify_profile
from typing import List
from app.schemas.students import StudentCreate, StudentOut
from app.schemas.teacher import TeacherOut
from app.schemas.services import ServiceOut
from app.models.teacher import Teacher
from app.models.services import Service
from app.services.gemini_service import extract_search_criteria
from sqlalchemy import or_, func

router = APIRouter(
    prefix="/students",
    tags=["students"],
)

@router.post("/", response_model=StudentOut)
def create_student_endpoint(student: StudentCreate, db: Session = Depends(get_db)):
  return create_student(db, student)

@router.get("/", response_model=List[StudentOut])
def get_students_endpoint(db: Session = Depends(get_db)):
  return get_students(db)

@router.delete("/")
def delete_all_students_endpoint(db: Session = Depends(get_db)):
  delete_all_students(db)
  return {"message": "All students deleted successfully"}

@router.put("/modify_password")
def modify_password_endpoint(
  old_password: str,
  new_password: str,
  email: str | None = None,
  student_username: str | None = None,
  db: Session = Depends(get_db)
):
  identifier = (email or student_username or "").strip()
  if not identifier:
    raise HTTPException(status_code=400, detail="email is required")
  return modify_password(db, identifier, old_password, new_password)

@router.put("/modify_profile")
def modify_profile_endpoint(educational_level: str, mobile_number: str, email: str, address: str, db: Session = Depends(get_db)):
  return modify_profile(db, educational_level, mobile_number, email, address)

@router.put("/change_personal_info")
def change_personal_info_endpoint(
  educational_level: str,
  phone_number: str,
  email: str,
  postal_address: str,
  db: Session = Depends(get_db)
):
  return modify_profile(db, educational_level, phone_number, email, postal_address)

@router.delete("/delete_profile/{student_email}")
def delete_profile_endpoint(student_email: str, student_password: str, db: Session = Depends(get_db)):
  if delete_student(db, student_email, student_password):
    return {"message": "Student profile deleted successfully"}
  raise HTTPException(status_code=404, detail="Student not found")

@router.get("/search/smart")
def smart_search(
  query: str,
  role: str | None = Query(default=None),
  db: Session = Depends(get_db)
):
  criteria = extract_search_criteria(query)
  if not criteria:
    criteria = {"role": "teacher"}

  # role can be forced by client when user explicitly selects teacher/service
  forced_role = (role or "").strip().lower()
  if forced_role in {"teacher", "service"}:
    criteria["role"] = forced_role

  search_role = criteria.get("role", "teacher")
  results = []

  if search_role == "teacher":
    query_db = db.query(Teacher).filter(func.lower(Teacher.status) == "active")

    if criteria.get("full_name"):
      query_db = query_db.filter(Teacher.full_name.ilike(f"%{criteria['full_name']}%"))

    if criteria.get("subject"):
      query_db = query_db.filter(Teacher.subject.ilike(f"%{criteria['subject']}%"))

    if criteria.get("level"):
      query_db = query_db.filter(Teacher.teachinglevel.ilike(f"%{criteria['level']}%"))

    if criteria.get("postal_address"):
      postal_address_term = criteria["postal_address"]
      query_db = query_db.filter(Teacher.postal_address.ilike(f"%{postal_address_term}%"))

    if criteria.get("availability"):
      query_db = query_db.filter(Teacher.location_mode.ilike(f"%{criteria['availability']}%"))

    if criteria.get("deplacement"):
      query_db = query_db.filter(Teacher.deplacemnt.ilike(f"%{criteria['deplacement']}%"))

    if criteria.get("domain"):
      query_db = query_db.filter(Teacher.domain.ilike(f"%{criteria['domain']}%"))

    raw_results = query_db.all()
    for teacher in raw_results:
      service_prices = [service.price for service in teacher.services if service.price is not None]
      min_price = min(service_prices) if service_prices else None
      
      # Calculate average rating
      ratings = [eval.note for eval in teacher.evaluations if eval.note is not None]
      avg_rating = sum(ratings) / len(ratings) if ratings else 0
      
      teacher_data = {
        "id": teacher.id,
        "full_name": teacher.full_name,
        "postal_address": teacher.postal_address,          "geo_coordinates": teacher.geo_coordinates,        "bio": teacher.bio,
        "subject": teacher.subject,
        "teaching_level": teacher.teachinglevel,
        "education_mode": teacher.location_mode,
        "profile_picture": teacher.profile_picture,
        "price": min_price,
        "rating": round(avg_rating, 1),
      }
      results.append(teacher_data)

  elif search_role == "service":
    query_db = db.query(Service)

    if criteria.get("subject"):
      subject_term = criteria["subject"]
      query_db = query_db.filter(
        or_(
          Service.name.ilike(f"%{subject_term}%"),
          Service.category.ilike(f"%{subject_term}%"),
          Service.description.ilike(f"%{subject_term}%")
        )
      )

    if criteria.get("category"):
      query_db = query_db.filter(Service.category.ilike(f"%{criteria['category']}%"))

    if criteria.get("level"):
      query_db = query_db.filter(Service.level.ilike(f"%{criteria['level']}%"))

    if criteria.get("name"):
      query_db = query_db.filter(Service.name.ilike(f"%{criteria['name']}%"))

    if criteria.get("price_value"):
      price_value = criteria["price_value"]
      operator = criteria.get("price_operator") or "<="
      if operator == "<":
        query_db = query_db.filter(Service.price < price_value)
      elif operator == ">":
        query_db = query_db.filter(Service.price > price_value)
      elif operator == ">=":
        query_db = query_db.filter(Service.price >= price_value)
      else:
        query_db = query_db.filter(Service.price <= price_value)

    raw_results = query_db.all()
    for service in raw_results:
      teacher = db.query(Teacher).filter(Teacher.id == service.teacher_id).first()
      service_data = {
        "id": service.id,
        "name": service.name,
        "category": service.category,
        "description": service.description,
        "level": service.level,
        "price": service.price,
        "duration": service.duration,
        "teacher_id": service.teacher_id,
        "teacher_name": teacher.full_name if teacher else "Teacher",
        "education_mode": teacher.location_mode if teacher else "Onsite",
        "geo_coordinates": teacher.geo_coordinates if teacher else None,
      }
      results.append(service_data)

  return {"criteria": criteria, "results": results}

@router.get("/{student_id}", response_model=StudentOut)
def get_student_endpoint(student_id: int, db: Session = Depends(get_db)):
  student = get_student(db, student_id)
  if not student:
    raise HTTPException(status_code=404, detail="Student not found")
  return student

@router.delete("/{student_email}")
def delete_student_endpoint(student_email: str, student_password: str, db: Session = Depends(get_db)):
  if delete_student(db, student_email, student_password):
    return {"message": "Student deleted successfully"}
  raise HTTPException(status_code=404, detail="Student not found")
