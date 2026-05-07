from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload
from app.models.parents import Parent
from app.models.users import User
from app.models.students import Student
from app.schemas.parents import ParentCreate
from app.schemas.students import ChildProfileCreate
from fastapi import HTTPException
from app.core.security import hash_password, password_matches

def create_parent(db:Session,parent:ParentCreate):
  if parent.password != parent.confirm_password:
    raise HTTPException(status_code=400, detail="Passwords do not match")

  hashed_password = hash_password(parent.password)
  
  existing_user = db.query(User).filter(User.email == parent.email).first()
  if existing_user:
    raise HTTPException(status_code=400, detail="Email already registered")
  
  data = parent.model_dump(exclude={'confirm_password'})
  db_parent=Parent(**data, type="Parent")
  db_parent.password=hashed_password
  db.add(db_parent)
  db.commit()
  db.refresh(db_parent)
  return db_parent

def add_child_to_parent(db: Session, parent_id: int, child_data: ChildProfileCreate):
  parent = db.query(Parent).filter(Parent.id == parent_id).first()
  if not parent:
    raise HTTPException(status_code=404, detail="Parent not found")
  
  # Check if email is provided and already exists (optional for children in this context but User requires it)
  if child_data.email:
    existing_user = db.query(User).filter(User.email == child_data.email).first()
    if existing_user:
      raise HTTPException(status_code=400, detail="Email already registered for this child")
  
  # For child profiles created by parents, we might want to default the email if not provided
  # However, User model usually needs an email. Let's see if we can use a placeholder or if it's required.
  # If it's a "classic student register", they usually have an email.
  
  student_data = child_data.model_dump(exclude={'confirm_password'})
  # If no password provided, maybe use parent's or a default? 
  # Let's assume the parent provides one since "register student classique"
  
  db_student = Student(
    **student_data,
    parent_id=parent_id,
    type="Student"
  )
  db.add(db_student)
  db.commit()
  db.refresh(db_student)
  return db_student

def get_parent(db:Session,parent_id:int):
  parent = (
    db.query(Parent)
    .options(selectinload(Parent.students))
    .filter(Parent.id == parent_id)
    .first()
  )
  return parent

def get_parents(db:Session):
  return db.query(Parent).options(selectinload(Parent.students)).all()

def delete_parent(db:Session,parent_username:str,parent_password:str):
  from app.models.messages import Messages
  from app.models.notifications import Notification

  user = db.query(User).filter((User.full_name==parent_username) | (User.email==parent_username)).first()
  if user and password_matches(parent_password, user.password):
    parent_id = user.id
    
    # Delete independent records
    db.query(Messages).filter((Messages.sender_id == parent_id) | (Messages.receiver_id == parent_id)).delete(synchronize_session=False)
    db.query(Notification).filter(Notification.user_id == parent_id).delete(synchronize_session=False)

    db.delete(user)
    db.commit()
    return True
  return False

def delete_all_parents(db:Session):
  db.query(Parent).delete()
  db.commit()