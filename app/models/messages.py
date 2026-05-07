from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from app.database.database import Base
from app.models.users import User
from sqlalchemy import ForeignKey
from sqlalchemy.orm  import relationship  
from datetime import datetime,timezone
class Messages(Base):
  __tablename__="messages"
  id=Column(Integer, primary_key=True, index=True)
  sender_id=Column(Integer,ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
  receiver_id=Column(Integer,ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
  time= Column(String, nullable=True)
  is_read=Column(Boolean, default=False)
  content=Column(String)
  timestamp=Column(DateTime, default=lambda: datetime.now(timezone.utc))
  sender=relationship("User", foreign_keys=[sender_id], backref="sent_messages")
  receiver=relationship("User", foreign_keys=[receiver_id], backref="received_messages")
