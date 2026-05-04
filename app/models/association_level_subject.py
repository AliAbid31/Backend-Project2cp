from sqlalchemy import Table, Column, Integer, ForeignKey
from app.database.database import Base

level_subjects = Table(
    "level_subjects",
    Base.metadata,
    Column("level_id", Integer, ForeignKey("levels.id", ondelete="CASCADE"), primary_key=True),
    Column("subject_id", Integer, ForeignKey("subjects.id", ondelete="CASCADE"), primary_key=True),
)
