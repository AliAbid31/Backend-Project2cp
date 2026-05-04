"""
Script to seed test sessions with proper future dates
"""
from datetime import datetime, timedelta
from app.database.database import SessionLocal
from app.models.teacher import Teacher
from app.models.session import Session as SessionModel

def seed_future_sessions():
    db = SessionLocal()
    
    try:
        # Find Yazen teacher
        yazen = db.query(Teacher).filter(Teacher.email == "tadjeddineahmed85@gmail.com").first()
        if not yazen:
            print("❌ Yazen not found")
            return
        
        print(f"✅ Found teacher: {yazen.full_name} (ID: {yazen.id})")
        
        # Delete old session first
        old_sessions = db.query(SessionModel).filter(SessionModel.teacher_id == yazen.id).all()
        print(f"Deleting {len(old_sessions)} old session(s)...")
        for session in old_sessions:
            db.delete(session)
        db.commit()
        
        # Create new future sessions
        base_date = datetime.now() + timedelta(days=1)
        
        sessions_data = [
            {
                "title": "English Conversation Class",
                "location": "Online",
                "start_hour": "10:00",
                "end_hour": "11:00",
                "date": base_date.strftime("%Y-%m-%d"),
                "price": 50,
                "status": "AVAILABLE",
            },
            {
                "title": "Advanced Grammar Lesson",
                "location": "In-Person",
                "start_hour": "14:00",
                "end_hour": "15:30",
                "date": (base_date + timedelta(days=2)).strftime("%Y-%m-%d"),
                "price": 60,
                "status": "AVAILABLE",
            },
            {
                "title": "Group Pronunciation Workshop",
                "location": "Online",
                "start_hour": "16:00",
                "end_hour": "17:00",
                "date": (base_date + timedelta(days=3)).strftime("%Y-%m-%d"),
                "price": 40,
                "status": "AVAILABLE",
            },
        ]
        
        for session_data in sessions_data:
            session = SessionModel(
                title=session_data["title"],
                location=session_data["location"],
                start_hour=session_data["start_hour"],
                end_hour=session_data["end_hour"],
                date=session_data["date"],
                price=session_data["price"],
                status=session_data["status"],
                teacher_id=yazen.id,
                service_id=None,
            )
            db.add(session)
            print(f"✅ Added: {session_data['title']} on {session_data['date']} at {session_data['start_hour']}")
        
        db.commit()
        print("\n✅ All sessions created successfully!")
        print("📅 Please refresh your app to see the sessions.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_future_sessions()
