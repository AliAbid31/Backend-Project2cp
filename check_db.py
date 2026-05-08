import sys
import os

# Set up path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from sqlalchemy import inspect
from app.database.database import engine

def check_db():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("Tables:", tables)
    if "password_resets" in tables:
        print("Table 'password_resets' exists.")
    else:
        print("Table 'password_resets' DOES NOT exist.")

if __name__ == "__main__":
    check_db()
