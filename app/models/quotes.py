from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from app.database.database import Base
from app.models.users import User
from app.models.association_student_quote import student_quote
from datetime import datetime

class Quote(Base):
  __tablename__="quotes"
  id=Column(Integer,primary_key=True,index=True)
  objectif=Column(String)
  frequence=Column(String)
  duration=Column(String)
  budget=Column(Float)
  subject=Column(String)
  level=Column(String)
  status=Column(String, default="pending", nullable=True)
  created_at=Column(DateTime, default=datetime.utcnow, nullable=True)
  updated_at=Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
  teacher_id=Column(Integer,ForeignKey('teachers.id'))
  teacher=relationship("Teacher", back_populates="quotes")
  students=relationship("Student", secondary=student_quote, back_populates="quotes")