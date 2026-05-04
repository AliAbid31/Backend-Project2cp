import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'tutoratup.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if payment columns exist in 'teachers' table
    cursor.execute("PRAGMA table_info(teachers)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'payment_method' not in columns:
        print("Adding 'payment_method' column to 'teachers' table...")
        cursor.execute("ALTER TABLE teachers ADD COLUMN payment_method VARCHAR")
        print("Column 'payment_method' added successfully.")
    else:
        print("Column 'payment_method' already exists in 'teachers' table.")
    
    if 'payment_info' not in columns:
        print("Adding 'payment_info' column to 'teachers' table...")
        cursor.execute("ALTER TABLE teachers ADD COLUMN payment_info VARCHAR")
        print("Column 'payment_info' added successfully.")
    else:
        print("Column 'payment_info' already exists in 'teachers' table.")
        
    conn.commit()
except Exception as e:
    print(f"Error updating database: {e}")
finally:
    conn.close()
