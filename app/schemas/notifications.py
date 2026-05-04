from pydantic import BaseModel, EmailStr
from app.schemas.users import UserBase
from datetime import datetime

class NotificationBase(BaseModel):
    message: str
    notification_type: str # e.g., "quote", "message", "session"

class NotificationOut(NotificationBase):
    id: int
    user_id: int
    is_seen: bool
    created_at: datetime

    class Config:
        from_attributes = True