from __future__ import annotations
from datetime import datetime

from pydantic import BaseModel, EmailStr
from app.schemas.session_audit import SessionAuditOut
from app.schemas.users import UserBase
from typing import Optional, List

class SessionBase(BaseModel):
  start_hour:str
  title:str
  location :str
  end_hour:str
  status:str
  date:str
  price:int
  service_id: Optional[int] = None

class SessionCreate(SessionBase):
  teacher_id:int

class SessionOut(SessionBase):
  id:int
  teacher_id:int
  audit_logs:List[SessionAuditOut]=[]
  class Config:
    from_attributes=True
class SessionCreateMultiple(BaseModel):
  service_id: int
  student_id: int
  sessions: List[SessionBase]

class SessionUpdate(BaseModel):
  reasons_for_cancellation: Optional[str] = None
  status: Optional[str] = None
  date: Optional[str] = None
  start_hour: Optional[str] = None
  end_hour: Optional[str] = None
  title: Optional[str] = None
  location: Optional[str] = None
  price: Optional[int] = None