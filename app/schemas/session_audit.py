from pydantic import BaseModel, EmailStr, model_validator
from datetime import datetime
class SessionAuditBase(BaseModel):
  reasons_for_cancellation:str
  status:str
class SessionAuditCreate(SessionAuditBase):
  pass
class SessionAuditOut(SessionAuditBase):
  id:int
  old_status:str
  changed_at:datetime
  session_id:int
  
  class Config:
    from_attributes=True   