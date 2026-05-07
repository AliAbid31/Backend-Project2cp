from sqlalchemy import Column, Integer, ForeignKey,Table
from app.database.database import Base
student_session=  Table('student_session',Base.metadata,
    Column('student_id', Integer, ForeignKey('students.id', ondelete='CASCADE'), primary_key=True),
    Column('session_id', Integer, ForeignKey('sessions.id', ondelete='CASCADE'), primary_key=True)
)
