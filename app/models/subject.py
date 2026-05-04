from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database.database import Base
from app.models.association_teacher_subjects import teacher_subjects
from app.models.association_level_subject import level_subjects


class Subject(Base):
  __tablename__ = "subjects"
  id = Column(Integer, primary_key=True, index=True)
  name = Column(String)
  teachers = relationship("Teacher", secondary=teacher_subjects, back_populates="subjects")
  levels = relationship("TeachingLevel", secondary=level_subjects, back_populates="subjects")
  