#!/usr/bin/env python3
"""
Test script to verify dashboard stats query logic
"""
import sys
sys.path.insert(0, '.')

from app.database.database import SessionLocal
from app.crud import crud_admin

def test_dashboard_stats():
    db = SessionLocal()
    try:
        stats = crud_admin.get_dashboard_stats(db)
        print("✅ Dashboard Stats Retrieved Successfully:")
        print(f"   Total Teachers: {stats['total_teachers']}")
        print(f"   Active Teachers: {stats['active_teachers']}")
        print(f"   Pending Teachers: {stats['pending_teachers']}")
        print(f"   Total Students: {stats['total_students']}")
        print(f"   Total Parents: {stats['total_parents']}")
        print(f"   Total Services: {stats['total_services']}")
        
        top_teachers = crud_admin.get_top_performing_teachers(db, limit=3)
        print(f"\n✅ Top Performing Teachers: {len(top_teachers)} found")
        for teacher in top_teachers:
            print(f"   - {teacher['full_name']}: {teacher['average_rating']}/5.0 ({teacher['evaluation_count']} reviews)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_dashboard_stats()
