from pydantic import BaseModel, EmailStr
from app.schemas.users import UserBase
from typing import Optional, List

from app.schemas.students import ChildProfileOut

class ParentBase(UserBase):
  referent_children: Optional[str] = None

class ParentCreate(ParentBase):
  full_name: str
  password: str
  confirm_password: str

class ParentOut(ParentBase):
  id: int
  full_name: str
  email: str
  phone_number: Optional[str] = None
  postal_address: Optional[str] = None
  students: Optional[List[ChildProfileOut]] = []

  class Config:
    from_attributes = True





  