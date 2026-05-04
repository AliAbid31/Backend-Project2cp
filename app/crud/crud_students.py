from sqlalchemy.orm import Session
from app.models.students import Student
from app.models.users import User
from app.schemas.students import StudentCreate
from fastapi import HTTPException
from app.core.security import hash_password, password_matches

def create_student(db:Session,student:StudentCreate):
  hashed_password=hash_password(student.password)

  if student.password != student.confirm_password:
    raise HTTPException(status_code=400, detail="Passwords do not match")
  
  existing_user = db.query(User).filter(User.email == student.email).first()
  if existing_user:
    raise HTTPException(status_code=400, detail="Email already registered")
  
  data = student.model_dump(exclude={'confirm_password'})
  db_student=Student(**data, type="Student")
  db_student.password=hashed_password
  db.add(db_student)
  db.commit()
  db.refresh(db_student)
  return db_student

def get_student(db:Session,student_id:int):
  student=db.query(Student).filter(Student.id==student_id).first()
  return student

def get_students(db:Session):
  return db.query(Student).all()

def delete_student(db:Session,student_email:str,student_password:str):
  student = db.query(Student).filter(Student.email==student_email).first()
  if student and password_matches(student_password, student.password):
    db.delete(student)
    db.commit()
    return True
  return False

def delete_all_students(db:Session):
  db.query(User).filter(User.type=='Student').delete()
  db.commit()

def modify_password(db:Session,student_email:str,old_password:str,new_password:str):
  student = db.query(Student).filter(Student.email==student_email).first()
  if student:
    if not password_matches(old_password, student.password):
      raise HTTPException(status_code=404, detail="Student not found or old password is incorrect")
    student.password = hash_password(new_password)
    db.add(student)
    db.commit()
    db.refresh(student)
    return student
  raise HTTPException(status_code=404, detail="Student not found or old password is incorrect")

def modify_profile(db: Session, educational_level: str, phone_number: str, email: str, postal_address: str):
  student = db.query(Student).filter(Student.email==email).first()
  if student:
    student.educational_level = educational_level
    student.phone_number = phone_number
    student.postal_address = postal_address
    student.email = email
    db.add(student)
    db.commit()
    db.refresh(student)
    return student

  raise HTTPException(status_code=404, detail="Student not found")

