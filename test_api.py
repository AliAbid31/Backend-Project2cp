#!/usr/bin/env python3
"""
Test the admin dashboard API endpoint
"""
import sys
sys.path.insert(0, '.')

from app.database.database import SessionLocal
from app.crud import crud_admin
from app.models.users import User
import json

def test_api():
    db = SessionLocal()
    try:
        # Get an admin user from the database to verify they exist
        admin = db.query(User).filter(User.type == "Admin").first()
        if admin:
            print(f"✅ Admin user found: {admin.email} (ID: {admin.id})")
        else:
            print("❌ No admin user found in database")
            # Create test admin if needed
            return
        
        # Test dashboard stats
        stats = crud_admin.get_dashboard_stats(db)
        print("\n✅ Dashboard Stats:")
        print(json.dumps(stats, indent=2))
        
        # Test top performing teachers
        teachers = crud_admin.get_top_performing_teachers(db, limit=3)
        print("\n✅ Top Performing Teachers:")
        print(json.dumps(teachers, indent=2))
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_api()
