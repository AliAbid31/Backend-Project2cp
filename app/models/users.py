from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database.database import Base

class User(Base):
  __tablename__="users"
  id=Column(Integer, primary_key=True, index=True)
  full_name=Column(String)
  email=Column(String, unique=True, index=True)
  phone_number=Column(String)
  postal_address=Column(String)
  geo_coordinates=Column(String)
  password=Column(String)
  token=Column(String)
  status=Column(String, default="active")  
  notifications=relationship("Notification", back_populates="user")
  type=Column(String(50))

  __mapper_args__ = {
        "polymorphic_identity": "User",
        "polymorphic_on": type,
    }