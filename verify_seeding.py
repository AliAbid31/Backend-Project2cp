import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")

engine = create_engine(DATABASE_URL)

with engine.connect() as connection:
    print("Levels with their subjects:")
    result = connection.execute(text("""
        SELECT l.name, string_agg(s.name, ', ') 
        FROM levels l
        JOIN level_subjects ls ON l.id = ls.level_id
        JOIN subjects s ON ls.subject_id = s.id
        GROUP BY l.name
    """))
    for row in result:
        print(f"{row[0]}: {row[1]}")
