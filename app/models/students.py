from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from app.database.database import Base
from app.models.users import User
from app.models.association_teacher_student import teacher_student
from app.models.association_student_quote import student_quote
from app.models.association_student_session import student_session
from app.models.association_student_service import student_service
from app.models.association_student_document import student_document

class Student(User):
  __tablename__="students"
  id=Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
  learning_objectives=Column(String)
  educational_level=Column(String)
  parent_id=Column(Integer, ForeignKey('parents.id'))
  parent=relationship("Parent", back_populates="students", foreign_keys=[parent_id])
  teacher=relationship("Teacher",secondary=teacher_student, back_populates="students", cascade="all")
  quotes=relationship("Quote",secondary=student_quote, back_populates="students", cascade="all")
  sessions=relationship("Session",secondary=student_session, back_populates="students", cascade="all")
  services=relationship("Service", secondary=student_service, back_populates="students", cascade="all")
  documents=relationship("Document", secondary=student_document, back_populates="students", cascade="all")
  received_reports=relationship("Report", back_populates="student", foreign_keys="Report.student_id")

  __mapper_args__ = {
        'polymorphic_identity': 'Student',
    }