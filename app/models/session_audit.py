from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from app.database.database import Base
class SessionAudit(Base):
  __tablename__="session_audit"
  id=Column(Integer,primary_key=True,index=True)
  session_id=Column(Integer,ForeignKey('sessions.id'))
  old_status=Column(String)
  new_status=Column(String)
  reasons_for_cancellation=Column(String,nullable=False)
  change_at=Column(DateTime)
  session=relationship("Session", back_populates="audits")
  