import os
from sqlalchemy import create_engine
from app.database.database import Base
from app.models.association_level_subject import level_subjects
from app.models.teaching_level import TeachingLevel
from app.models.subject import Subject
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")

engine = create_engine(DATABASE_URL)

# Create the new table
Base.metadata.create_all(bind=engine)
print("Database schema updated.")
