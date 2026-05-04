from sqlalchemy import Column, Integer, ForeignKey, String
from app.database.database import Base
from app.models.users import User


class Admin(User):
    __tablename__ = "admins"
    id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    admin_level = Column(String, default="super")  # super, moderator, etc.

    __mapper_args__ = {
        'polymorphic_identity': 'Admin',
    }
