from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from app.database.database import Base
from app.models.users import User
from sqlalchemy import ForeignKey
from sqlalchemy.orm  import relationship  
class Certificate(Base):
  __tablename__="certificates"
  id=Column(Integer, primary_key=True, index=True)
  name=Column(String)
  file_path=Column(String)
  title=Column(String)
  
  
  teacher_id=Column(Integer,ForeignKey('teachers.id'))
  teacher=relationship("Teacher", back_populates="certificates")