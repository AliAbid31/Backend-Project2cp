import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from app.core.config import settings


SQLALCHEMY_DATABASE_URL = settings.get_database_url

# Create the Engine with better connection handling
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={
        "connect_timeout": 10,
        "options": "-c statement_timeout=30000"
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    try:
        with engine.connect() as connection:
            print("✅ Connected to PostgreSQL successfully!")
    except Exception as e:
        print("❌ Connection failed. Check if pgAdmin has the database 'tutorly_db' created.")
        print(f"Error details: {e}")