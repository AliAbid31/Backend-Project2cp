from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DocumentBase(BaseModel):
  title: str
  type: str  # 'Courses', 'Exercises', 'Homework', 'Other'
  description: str
  date: str
  teacher_id: int
  drive_url: Optional[str] = None
  service_id: Optional[int] = None
  session_id: Optional[int] = None

class DocumentCreate(DocumentBase):
  pass

class DocumentUpload(BaseModel):
  title: str
  type: str  # 'Courses', 'Exercises', 'Homework', 'Other'
  description: str
  date: str
  teacher_id: int
  drive_url: Optional[str] = None
  service_id: Optional[int] = None
  session_id: Optional[int] = None

class DocumentOut(DocumentBase):
  id: int
  file_path: Optional[str] = None
  file_size: Optional[int] = None
  created_at: Optional[datetime] = None
  drive_url: Optional[str] = None
  
  class Config:
    from_attributes = True

class DocumentSearchResult(BaseModel):
  id: int
  title: str
  type: str
  description: str
  date: str
  teacher_id: int
  file_path: Optional[str] = None
  drive_url: Optional[str] = None
  drive_file_id: Optional[str] = None
  file_size: Optional[int] = None
  created_at: Optional[datetime] = None
  
  class Config:
    from_attributes = True