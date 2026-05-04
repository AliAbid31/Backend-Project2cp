from pydantic import BaseModel, EmailStr
from app.schemas.users import UserBase
from typing import List, Optional
from datetime import datetime

class StudentInQuote(BaseModel):
    id: int
    full_name: str
    educational_level: Optional[str] = None
    postal_address: Optional[str] = None
    profile_picture: Optional[str] = None
    
    class Config:
        from_attributes = True

class QuoteBase(BaseModel):
  objectif:str
  frequence:str
  duration:str
  budget:float
  subject:str
  level:str

class QuoteCreate(QuoteBase):
  teacher_id: int
  student_id: Optional[int] = None

class QuoteOut(QuoteBase):
  id:int
  teacher_id: int
  status: str = "pending"
  students: List[StudentInQuote] = []
  created_at: Optional[datetime] = None
  updated_at: Optional[datetime] = None
  
  class Config:
    from_attributes=True 