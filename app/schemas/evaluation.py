from pydantic import BaseModel
from typing import Optional

class EvaluationBase(BaseModel):
  comment: str
  date: str
  note: float
  evaluator_id: int
  session_id: Optional[int] = None

class EvaluationCreate(EvaluationBase):
  teacher_id: int

class EvaluationOut(EvaluationBase):
  id: int
  teacher_id: int
  student_name: Optional[str] = None
  student_avatar: Optional[str] = None
  rating: Optional[float] = None # Alias for note for frontend compatibility
  
  
  
  class Config:
    from_attributes = True