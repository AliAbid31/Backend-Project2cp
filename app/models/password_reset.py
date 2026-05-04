from sqlalchemy import Column, Integer, String, DateTime
from app.database.database import Base
from datetime import datetime, timedelta

class PasswordReset(Base):
    __tablename__ = "password_resets"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    token = Column(String, unique=True, index=True)
    expires = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)