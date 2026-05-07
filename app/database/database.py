import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


SQLALCHEMY_DATABASE_URL = settings.get_database_url

# Create the Engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=5,        # Keeps 5 connections open for speed
    max_overflow=10     # Can open 10 more if the app gets busy
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    try:
        # This is a great "Health Check" script
        with engine.connect() as connection:
            print("✅ Connected to PostgreSQL successfully!")
    except Exception as e:
        print("❌ Connection failed. Check if pgAdmin has the database 'tutorly_db' created.")
        print(f"Error details: {e}")