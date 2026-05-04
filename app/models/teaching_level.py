from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database.database import Base
from app.models.association_teacher_level import teacher_levels
from app.models.association_level_subject import level_subjects


class TeachingLevel(Base):
  __tablename__ = "levels"
  id = Column(Integer, primary_key=True, index=True)
  name = Column(String)
  teachers = relationship("Teacher", secondary=teacher_levels, back_populates="levels")
  subjects = relationship("Subject", secondary=level_subjects, back_populates="levels")
