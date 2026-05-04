from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

from app.database.database import Base


class TeacherApplication(Base):
    __tablename__ = "teacher_applications"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, index=True, nullable=False)
    phone_number = Column(String)
    postal_address = Column(String)
    geo_coordinates = Column(String)
    password = Column(String, nullable=False)
    subject = Column(String)
    teachinglevel = Column(String)
    location_mode = Column(String)
    deplacemnt = Column(String)
    nature = Column(String)
    domain = Column(String)
    profile_picture = Column(String)
    bio = Column(String)
    payment_method = Column(String)
    payment_info = Column(String)
    status = Column(String, default="pending", index=True)
    certificates_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)

