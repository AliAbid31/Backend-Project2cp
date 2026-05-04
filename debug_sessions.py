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
        # List all teachers first
        print("📋 All teachers in database:")
        teachers = db.query(Teacher).all()
        for t in teachers:
            sessions_count = db.query(SessionModel).filter(SessionModel.teacher_id == t.id).count()
            print(f"  ID: {t.id}, Name: '{t.full_name}', Email: {t.email}, Sessions: {sessions_count}")
        
        # Find Yazen teacher by email
        yazen = db.query(Teacher).filter(Teacher.email == "tadjeddineahmed85@gmail.com").first()
        if not yazen:
            print("\n❌ Could not find teacher with email tadjeddineahmed85@gmail.com")
            return
        
        print(f"\n✅ Found teacher: '{yazen.full_name}' (ID: {yazen.id})")
        
        # Get all sessions for Yazen
        sessions = db.query(SessionModel).filter(SessionModel.teacher_id == yazen.id).all()
        print(f"📊 Total sessions: {len(sessions)}")
        
        now = datetime.now()
        print(f"📅 Current date/time: {now}")
        
        for session in sessions:
            print(f"\n---")
            print(f"Session ID: {session.id}")
            print(f"Title: {session.title}")
            print(f"Date (raw): {repr(session.date)}")
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
        import traceback
        print(f"❌ Error: {e}")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_sessions()
