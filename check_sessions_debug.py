"""
Debug script to check sessions in the database
"""
from app.database.database import SessionLocal
from app.models.teacher import Teacher
from app.models.session import Session as SessionModel
from datetime import datetime

def check_sessions():
    db = SessionLocal()
    
    try:
        # Find Yazen teacher
        yazen = db.query(Teacher).filter(Teacher.full_name == "Yazen").first()
        if not yazen:
            print("❌ Yazen not found")
            return
        
        print(f"✅ Found teacher: {yazen.full_name} (ID: {yazen.id})")
        
        # Get all sessions for Yazen
        sessions = db.query(SessionModel).filter(SessionModel.teacher_id == yazen.id).all()
        print(f"\n📊 Total sessions: {len(sessions)}")
        
        now = datetime.now()
        print(f"📅 Current date/time: {now}")
        
        for session in sessions:
            print(f"\n---")
            print(f"Session ID: {session.id}")
            print(f"Title: {session.title}")
            print(f"Date (raw): {session.date}")
            print(f"Date type: {type(session.date)}")
            print(f"Start: {session.start_hour}")
            print(f"Status: {session.status}")
            
            # Try to parse the date
            try:
                if isinstance(session.date, str):
                    session_date = datetime.strptime(session.date, "%Y-%m-%d")
                else:
                    session_date = session.date
                
                print(f"Parsed date: {session_date}")
                print(f"Is future: {session_date >= now}")
                print(f"Is not canceled: {session.status != 'Canceled'}")
            except Exception as e:
                print(f"❌ Parse error: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_sessions()
