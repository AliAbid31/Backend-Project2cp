from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from app.database.database import Base
from app.models.users import User
from app.models.association_student_service import student_service

class Service(Base):
  __tablename__="services"
  id=Column(Integer,primary_key=True,index=True)
  name=Column(String)  # Service Title
  category=Column(String) # Category (education_domain)
  description=Column(String)
  level=Column(String) # Target Level
  price=Column(Integer) # Price / Session
  start_date=Column(String)
  end_date=Column(String)
  number_of_sessions=Column(Integer)
  duration=Column(Integer) # Duration in minutes
  type=Column(String, default="One-on-One") # 'One-on-One' or 'Workshop'
  
  sessions=relationship("Session", back_populates="service")
  documents=relationship("Document", back_populates="service", cascade="all, delete-orphan")
  teacher_id=Column(Integer,ForeignKey('teachers.id'))
  teacher=relationship("Teacher", back_populates="services")
  students=relationship("Student", secondary=student_service, back_populates="services")