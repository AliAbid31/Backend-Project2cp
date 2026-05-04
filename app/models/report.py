from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship  
from app.database.database import Base
from app.models.users import User

class Report(Base):
  __tablename__="reports"
  id=Column(Integer, primary_key=True, index=True)
  report_type=Column(String)
  description=Column(String)
  reason=Column(String)
  screenshot_path=Column(String)
  reporter_id=Column(Integer, ForeignKey('users.id'))
  reporter=relationship("User", foreign_keys=[reporter_id])
  teacher_id=Column(Integer, ForeignKey('teachers.id'), nullable=True)
  student_id=Column(Integer, ForeignKey('students.id'), nullable=True)
  evaluation_id=Column(Integer, ForeignKey('evaluations.id'), nullable=True)
  teacher=relationship("Teacher", back_populates="received_reports", foreign_keys=[teacher_id])
  student=relationship("Student", back_populates="received_reports", foreign_keys=[student_id])
  evaluation=relationship("Evaluation", foreign_keys=[evaluation_id])