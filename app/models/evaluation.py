from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from app.database.database import Base
from app.models.users import User

class Evaluation(Base):
  __tablename__="evaluations"
  id=Column(Integer, primary_key=True, index=True)
  comment=Column(String)
  date=Column(String)
  note=Column(Float)
  teacher_id=Column(Integer, ForeignKey('teachers.id', ondelete='CASCADE'))
  teacher=relationship("Teacher", back_populates="evaluations", foreign_keys=[teacher_id])
  
  evaluator_id=Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
  evaluator=relationship("User", foreign_keys=[evaluator_id])
  
  session_id=Column(Integer, ForeignKey('sessions.id'), nullable=True)  # Session where evaluation occurred
  