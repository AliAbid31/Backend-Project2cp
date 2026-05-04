"""
Migration script to add status and timestamp columns to quotes table
"""
import sqlite3

def migrate_quotes_table():
    try:
        conn = sqlite3.connect('tutoratup.db')
        cursor = conn.cursor()
        
        # Check if status column exists
        cursor.execute("PRAGMA table_info(quotes)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'status' not in columns:
            print("Adding 'status' column to quotes table...")
            cursor.execute("ALTER TABLE quotes ADD COLUMN status VARCHAR DEFAULT 'pending'")
            print("✓ Added 'status' column")
        else:
            print("✓ 'status' column already exists")
        
        if 'created_at' not in columns:
            print("Adding 'created_at' column to quotes table...")
            cursor.execute("ALTER TABLE quotes ADD COLUMN created_at DATETIME")
            print("✓ Added 'created_at' column")
        else:
            print("✓ 'created_at' column already exists")
        
        if 'updated_at' not in columns:
            print("Adding 'updated_at' column to quotes table...")
            cursor.execute("ALTER TABLE quotes ADD COLUMN updated_at DATETIME")
            print("✓ Added 'updated_at' column")
        else:
            print("✓ 'updated_at' column already exists")
        
        conn.commit()
        conn.close()
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate_quotes_table()
