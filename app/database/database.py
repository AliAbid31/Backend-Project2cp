import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# 1. Database URL configuration
# Render provides DATABASE_URL. Neon URLs sometimes need the protocol adjusted.
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if SQLALCHEMY_DATABASE_URL:
    # SQLAlchemy requires "postgresql://" but some providers give "postgres://"
    if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    # Fallback to the hardcoded Neon URL
    SQLALCHEMY_DATABASE_URL = "postgresql://neondb_owner:npg_gPOle6ILzyo4@ep-cool-river-alupwxo5-pooler.c-3.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"


# 2. Create the Engine
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