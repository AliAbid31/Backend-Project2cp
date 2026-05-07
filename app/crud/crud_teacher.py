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
  from app.models.services import Service
  from app.models.session import Session
  from app.models.certificates import Certificate
  from app.models.quotes import Quote
  from app.models.evaluation import Evaluation
  from app.models.documents import Document
  from app.models.report import Report
  from app.models.messages import Messages
  from app.models.notifications import Notification
  from app.models.session_audit import SessionAudit

  user = db.query(User).filter(User.email==teacher_email).first()
  if user and password_matches(teacher_password, user.password):
    teacher_id = user.id
    
    # 1. Gather IDs
    teacher_sessions = db.query(Session).filter(Session.teacher_id == teacher_id).all()
    session_ids = [s.id for s in teacher_sessions]
    
    teacher_services = db.query(Service).filter(Service.teacher_id == teacher_id).all()
    service_ids = [s.id for s in teacher_services]

    # 2. Clear Associations (Many-to-Many)
    from app.models.association_teacher_student import teacher_student
    from app.models.association_student_session import student_session
    from app.models.association_student_service import student_service
    from app.models.association_student_document import student_document
    from app.models.association_student_quote import student_quote

    db.execute(teacher_student.delete().where(teacher_student.c.teacher_id == teacher_id))
    if session_ids:
        db.execute(student_session.delete().where(student_session.c.session_id.in_(session_ids)))
    if service_ids:
        db.execute(student_service.delete().where(student_service.c.service_id.in_(service_ids)))

    # 3. Delete linked records in CORRECT ORDER (children first)
    # Documents reference Teacher, Service, and Session
    db.query(Document).filter(Document.teacher_id == teacher_id).delete(synchronize_session=False)
    
    # SessionAudits reference Session
    if session_ids:
        db.query(SessionAudit).filter(SessionAudit.session_id.in_(session_ids)).delete(synchronize_session=False)
    
    # Sessions reference Service and Teacher
    db.query(Session).filter(Session.teacher_id == teacher_id).delete(synchronize_session=False)
    
    # Services reference Teacher
    db.query(Service).filter(Service.teacher_id == teacher_id).delete(synchronize_session=False)
    
    # Other independent records
    db.query(Evaluation).filter((Evaluation.teacher_id == teacher_id) | (Evaluation.evaluator_id == teacher_id)).delete(synchronize_session=False)
    db.query(Report).filter((Report.teacher_id == teacher_id) | (Report.reporter_id == teacher_id)).delete(synchronize_session=False)
    db.query(Certificate).filter(Certificate.teacher_id == teacher_id).delete(synchronize_session=False)
    db.query(Quote).filter(Quote.teacher_id == teacher_id).delete(synchronize_session=False)
    db.query(Messages).filter((Messages.sender_id == teacher_id) | (Messages.receiver_id == teacher_id)).delete(synchronize_session=False)
    db.query(Notification).filter(Notification.user_id == teacher_id).delete(synchronize_session=False)

    # 4. Finally delete the user
    db.delete(user)
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
    if teacher.postal_address != postal_address:
      teacher.postal_address = postal_address
      # Automatically update coordinates if address changed
      coords = get_lat_lng_from_address(postal_address)
      if coords:
        teacher.geo_coordinates = f"{coords[0]},{coords[1]}"
    
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
