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
  notifications=relationship("Notification", back_populates="user", cascade="all, delete-orphan")
  sent_messages = relationship("Messages", foreign_keys="[Messages.sender_id]", cascade="all, delete-orphan", passive_deletes=True)
  received_messages = relationship("Messages", foreign_keys="[Messages.receiver_id]", cascade="all, delete-orphan", passive_deletes=True)
  reports_made = relationship("Report", foreign_keys="[Report.reporter_id]", cascade="all, delete-orphan", passive_deletes=True)
  type=Column(String(50))

  __mapper_args__ = {
        "polymorphic_identity": "User",
        "polymorphic_on": type,
    }