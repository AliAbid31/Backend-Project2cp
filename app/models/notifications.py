from sqlalchemy import Column, DateTime, Integer, String, Boolean, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from app.database.database import Base  
from datetime import datetime,timezone
class Notification(Base):
  __tablename__="notifications"
  id=Column(Integer, primary_key=True, index=True)
  user_id=Column(Integer,ForeignKey('users.id'))
  user=relationship("User", back_populates="notifications")
  message=Column(String,nullable=False)
  notification_type=Column(String, nullable=False)
  is_seen=Column(Boolean, default=False)
  created_at=Column(DateTime, default=datetime.now(timezone.utc))
  timetamps=Column(DateTime, default=func.now())