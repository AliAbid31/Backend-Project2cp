from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from app.database.database import Base
from app.models.users import User
from sqlalchemy import ForeignKey
from sqlalchemy.orm  import relationship  
from app.models.association_teacher_student import teacher_student
from app.models.association_teacher_subjects import teacher_subjects
from app.models.association_teacher_level import teacher_levels

class Teacher(User):
  __tablename__="teachers"
  id=Column(Integer, ForeignKey('users.id'), primary_key=True)
  location_mode=Column(String)
  deplacemnt=Column(String)
  nature=Column(String)
  domain=Column(String)
  profile_picture=Column(String)
  bio=Column(String)
  subject=Column(String)
  teachinglevel=Column(String)
  payment_method=Column(String)
  payment_info=Column(String)

  quotes=relationship("Quote", back_populates="teacher", cascade="all, delete-orphan", passive_deletes=True)
  services=relationship("Service", back_populates="teacher", cascade="all, delete-orphan", passive_deletes=True)
  sessions=relationship("Session", back_populates="teacher", cascade="all, delete-orphan", passive_deletes=True)
  documents=relationship("Document", back_populates="teacher", cascade="all, delete-orphan", passive_deletes=True)
  evaluations=relationship("Evaluation", back_populates="teacher", foreign_keys="[Evaluation.teacher_id]", cascade="all, delete-orphan", passive_deletes=True)
  students=relationship("Student",secondary=teacher_student, back_populates="teacher")
  certificates=relationship("Certificate", back_populates="teacher", cascade="all, delete-orphan", passive_deletes=True)
  subjects=relationship("Subject", secondary=teacher_subjects, back_populates="teachers")
  levels=relationship("TeachingLevel", secondary=teacher_levels, back_populates="teachers")
  received_reports=relationship("Report", back_populates="teacher", foreign_keys="[Report.teacher_id]", cascade="all, delete-orphan", passive_deletes=True)

  __mapper_args__ = {
        'polymorphic_identity': 'Teacher',
    }