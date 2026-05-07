from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from app.database.database import Base
from app.models.users import User
from app.models.association_student_document import student_document
from datetime import datetime

class Document(Base):
  __tablename__="documents"
  id=Column(Integer, primary_key=True, index=True)
  title=Column(String)
  type=Column(String)
  description=Column(String)
  file_path=Column(String)
  file_size=Column(Integer, nullable=True)
  date=Column(String)
  created_at=Column(DateTime, default=datetime.utcnow)
  drive_url=Column(String, nullable=True)
  
  teacher_id=Column(Integer, ForeignKey('teachers.id', ondelete='CASCADE'))
  service_id=Column(Integer, ForeignKey('services.id', ondelete='CASCADE'), nullable=True)
  session_id=Column(Integer, ForeignKey('sessions.id', ondelete='CASCADE'), nullable=True)
  
  teacher=relationship("Teacher", back_populates="documents")
  service=relationship("Service", back_populates="documents")
  session=relationship("Session", backref="documents")
  students=relationship("Student", secondary=student_document, back_populates="documents")
  