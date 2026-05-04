import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'tutoratup.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Rename report_reason to reason
    cursor.execute("PRAGMA table_info(reports)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'report_reason' in columns and 'reason' not in columns:
        print("Renaming 'report_reason' to 'reason'...")
        cursor.execute("ALTER TABLE reports RENAME COLUMN report_reason TO reason")
        print("Column renamed successfully.")
    
    # Rename scereenshot_path to screenshot_path
    if 'scereenshot_path' in columns and 'screenshot_path' not in columns:
        print("Renaming 'scereenshot_path' to 'screenshot_path'...")
        cursor.execute("ALTER TABLE reports RENAME COLUMN scereenshot_path TO screenshot_path")
        print("Column renamed successfully.")
        
    conn.commit()
except Exception as e:
    print(f"Error updating database: {e}")
finally:
    conn.close()
