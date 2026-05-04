from pydantic import BaseModel, EmailStr
from app.schemas.users import UserBase
from datetime import datetime,timezone
from typing import Optional

class MessageBase(BaseModel):
    sender_id: int
    receiver_id: int
    content: str
    time: Optional[str] = None


class MessageCreate(MessageBase):
    pass

#
class MessageOut(MessageBase):
    id: int
    sender_id: int
    timestamp: datetime
    is_read: bool

    class Config:
        from_attributes = True