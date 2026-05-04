from pydantic import BaseModel, EmailStr
from app.schemas.certificates import CertificateOut, CertificateCreate
from app.schemas.users import UserBase
from typing import Optional, List

class TeacherBase(UserBase):
  subject: Optional[str] = None
  teachinglevel: Optional[str] = None
  location_mode: Optional[str] = None
  deplacemnt: Optional[str] = None
  nature: Optional[str] = None
  domain: Optional[str] = None
  profile_picture: Optional[str] = None
  bio: Optional[str] = None
  payment_method: Optional[str] = None
  payment_info: Optional[str] = None
  

class TeacherCreate(TeacherBase):
  full_name: str
  password: str
  confirm_password: str
  certificates: Optional[List[CertificateCreate]] = []

class TeacherOut(TeacherBase):
  id: int
  full_name: str
  email: str
  phone_number: str
  postal_address: str
  geo_coordinates: Optional[str] = None
  certificates: list[CertificateOut] = []
  bio: Optional[str] = None

  class Config:
    from_attributes = True


