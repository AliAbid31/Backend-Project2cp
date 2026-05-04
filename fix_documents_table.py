#!/usr/bin/env python3
"""
Fix documents table by adding session_id column if missing
"""
import sqlite3
import sys

DB_PATH = "tutoratup.db"

def fix_documents_table():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if session_id column exists
        cursor.execute("PRAGMA table_info(documents)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "session_id" in columns:
            print("✓ session_id column already exists")
        else:
            print("✗ session_id column missing, adding it...")
            cursor.execute("""
                ALTER TABLE documents 
                ADD COLUMN session_id INTEGER 
                REFERENCES sessions(id)
            """)
            conn.commit()
            print("✓ Added session_id column to documents table")
        
        # Verify the column exists now
        cursor.execute("PRAGMA table_info(documents)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"✓ Documents table columns: {columns}")
        
        conn.close()
        print("\n✓ Database fix completed successfully!")
        
    except Exception as e:
        print(f"✗ Error fixing database: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    fix_documents_table()
