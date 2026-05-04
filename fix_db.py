import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'tutoratup.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if 'token' column exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'token' not in columns:
        print("Adding 'token' column to 'users' table...")
        cursor.execute("ALTER TABLE users ADD COLUMN token VARCHAR")
        print("Column 'token' added successfully.")
    else:
        print("Column 'token' already exists.")
        
    conn.commit()
except Exception as e:
    print(f"Error updating database: {e}")
finally:
    conn.close()
