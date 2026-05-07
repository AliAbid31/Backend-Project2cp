from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.teacher import Teacher
from app.models.users import User
from app.models.certificates import Certificate
from app.models.teacher_application import TeacherApplication
from app.schemas.teacher import TeacherCreate
from fastapi import HTTPException
from app.utils.google_maps import get_lat_lng_from_address
from app.core.security import hash_password, password_matches
import json

def create_teacher(db:Session,teacher:TeacherCreate):
  if teacher.password != teacher.confirm_password:
    raise HTTPException(status_code=400, detail="Passwords do not match")

  hashed_password = hash_password(teacher.password)
  
  normalized_email = (teacher.email or "").strip().lower()
  existing_user = db.query(User).filter(func.lower(User.email) == normalized_email).first()
  if existing_user:
    raise HTTPException(status_code=400, detail="Email already registered")
  
  data = teacher.model_dump(exclude={'confirm_password', 'certificates'})
  certificates_data = teacher.certificates or []
  
  if "postal_address" in data and data["postal_address"]:
    coords = get_lat_lng_from_address(data["postal_address"])
    if coords:
      # On garde l'adresse lisible dans postal_address 
      # et on met les coordonnées dans geo_coordinates
      data["geo_coordinates"] = f"{coords[0]},{coords[1]}"
      
  existing_app = db.query(TeacherApplication).filter(func.lower(TeacherApplication.email) == normalized_email).first()
  if existing_app:
      raise HTTPException(status_code=400, detail="Une demande pour cet email est déjà en cours. Veuillez vérifier vos emails ou attendre la validation.")

  payload = {
    **data,
    "password": hashed_password,
    "status": "pending",
    "certificates_json": json.dumps(
      [cert.model_dump() for cert in certificates_data],
      ensure_ascii=True
    ),
  }
  db_teacher = TeacherApplication(**payload)
  db.add(db_teacher)
  db.commit()
  db.refresh(db_teacher)

  return db_teacher

def get_teacher(db:Session,teacher_id:int):
  teacher=db.query(Teacher).filter(Teacher.id==teacher_id).first()
  return teacher

def get_teachers(db:Session):
  return db.query(Teacher).all()

def delete_teacher(db:Session,teacher_email:str,teacher_password:str):
  teacher = db.query(Teacher).filter(Teacher.email==teacher_email).first()
  if teacher and password_matches(teacher_password, teacher.password):
    db.delete(teacher)
    db.commit()
    return True
  return False

def delete_all_teachers(db:Session):
  db.query(Teacher).delete()
  db.commit()

def modify_password(db: Session, teacher_email: str, old_password: str, new_password: str):
  teacher = db.query(Teacher).filter(Teacher.email==teacher_email).first()
  if teacher:
    if not password_matches(old_password, teacher.password):
      raise HTTPException(status_code=404, detail="Teacher not found or old password is incorrect")
    teacher.password = hash_password(new_password)
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher
  raise HTTPException(status_code=404, detail="Teacher not found or old password is incorrect")

def modify_profile(db: Session, bio: str, domain: str, subject: str, teachinglevel: str, education_mode: str, postal_address: str, email: str, profile_picture: str | None = None):
  teacher = db.query(Teacher).filter(Teacher.email==email).first()
  if teacher:
    teacher.bio = bio
    teacher.domain = domain
    teacher.subject = subject
    teacher.teachinglevel = teachinglevel
    teacher.location_mode = education_mode
    teacher.postal_address = postal_address
    if profile_picture is not None:
      teacher.profile_picture = profile_picture
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher
  raise HTTPException(status_code=404, detail="Teacher not found")
def update_payment_method(db: Session, email: str, payment_method: str, payment_info: str):
  teacher = db.query(Teacher).filter(Teacher.email==email).first()
  if teacher:
    teacher.payment_method = payment_method
    teacher.payment_info = payment_info
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher
  raise HTTPException(status_code=404, detail="Teacher not found")

def get_top_rated_teachers(db: Session, limit: int = 3):
    from app.models.evaluation import Evaluation
    from sqlalchemy import desc
    
    # Calculate average rating for each teacher
    results = db.query(
        Teacher,
        func.avg(Evaluation.note).label('average_rating')
    ).join(Evaluation, Teacher.id == Evaluation.teacher_id)\
    .group_by(Teacher.id)\
    .order_by(desc('average_rating'))\
    .limit(limit)\
    .all()
    
    # Format results to include average_rating in the teacher object or return as pairs
    top_teachers = []
    for teacher, avg_rating in results:
        # Attach the rating dynamically for the response
        teacher.average_rating = round(float(avg_rating), 1) if avg_rating else 0.0
        top_teachers.append(teacher)
        
    return top_teachers
