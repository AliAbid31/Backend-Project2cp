from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from app.schemas.users import UserBase

class StudentBase(UserBase):
  learning_objectives: Optional[str] = None
  educational_level: Optional[str] = None
  full_name: Optional[str] = None
  parent_id: Optional[int] = None

class StudentCreate(StudentBase):
  password: str
  confirm_password: str

class StudentOut(StudentBase):
  id: int
  parent_id: Optional[int] = None
  model_config = ConfigDict(from_attributes=True)

class ChildProfileCreate(BaseModel):
  full_name: str
  educational_level: str
  learning_objectives: str
  email: Optional[EmailStr] = None
  password: Optional[str] = None
  confirm_password: Optional[str] = None

class ChildProfileOut(BaseModel):
  id: int
  full_name: str
  educational_level: str
  learning_objectives: str
  model_config = ConfigDict(from_attributes=True)