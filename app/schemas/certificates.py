from typing import Optional

from pydantic import BaseModel, EmailStr
from app.schemas.users import UserBase
class CertificateBase(BaseModel):
  title: Optional[str] = None

class CertificateCreate(CertificateBase):
  file_path: str

class CertificateOut(CertificateBase):
  id:int
  
  file_path:str
  teacher_id:int
  class Config:
    from_attributes=True
  