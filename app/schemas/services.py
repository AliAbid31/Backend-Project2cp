from pydantic import BaseModel
from typing import Optional

class ServiceBase(BaseModel):
    name: str
    category: str
    description: str
    level: str
    price: int
    start_date: str
    end_date: str
    number_of_sessions: int
    duration: Optional[int] = None
    type: Optional[str] = "One-on-One" # "One-on-One" or "Workshop"

class ServiceCreate(ServiceBase):
    teacher_id: int

class ServiceOut(ServiceBase):
    id: int
    teacher_id: int

    class Config:
        from_attributes = True