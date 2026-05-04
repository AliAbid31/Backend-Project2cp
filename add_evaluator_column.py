import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'tutoratup.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("PRAGMA table_info(evaluations)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'evaluator_id' not in columns:
        print("Adding 'evaluator_id' column to 'evaluations' table...")
        cursor.execute("ALTER TABLE evaluations ADD COLUMN evaluator_id INTEGER REFERENCES users(id)")
        print("Column 'evaluator_id' added successfully.")
    else:
        print("Column 'evaluator_id' already exists in 'evaluations' table.")
        
    conn.commit()
except Exception as e:
    print(f"Error updating database: {e}")
finally:
    conn.close()
