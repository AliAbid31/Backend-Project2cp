import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")

engine = create_engine(DATABASE_URL)

with engine.connect() as connection:
    result = connection.execute(text("SELECT * FROM levels"))
    levels = result.fetchall()
    print("Levels:", levels)
    
    result = connection.execute(text("SELECT * FROM subjects"))
    subjects = result.fetchall()
    print("Subjects count:", len(subjects))
