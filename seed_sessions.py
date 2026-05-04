"""
Script to seed test sessions for teachers
"""
from datetime import datetime, timedelta
from app.database.database import SessionLocal
from app.models.teacher import Teacher
from app.models.session import Session as SessionModel

def seed_sessions():
    db = SessionLocal()
    
    try:
        # Find all teachers
        teachers = db.query(Teacher).all()
        print(f"Found {len(teachers)} teachers")
        
        for teacher in teachers:
            print(f"\nSeeding sessions for teacher: {teacher.full_name} (ID: {teacher.id})")
            
            # Check if teacher already has sessions
            existing = db.query(SessionModel).filter(SessionModel.teacher_id == teacher.id).count()
            print(f"  Existing sessions: {existing}")
            
            if existing == 0:
                # Create 3 test sessions
                base_date = datetime.now() + timedelta(days=1)
                
                sessions_data = [
                    {
                        "title": f"Math Lesson - {teacher.subject or 'General'}",
                        "location": "Online",
                        "start_hour": "10:00",
                        "end_hour": "11:00",
                        "date": base_date.strftime("%Y-%m-%d"),
                        "price": 50,
                        "status": "Available",
                    },
                    {
                        "title": f"Tutorial - {teacher.subject or 'General'}",
                        "location": "In-Person",
                        "start_hour": "14:00",
                        "end_hour": "15:30",
                        "date": (base_date + timedelta(days=2)).strftime("%Y-%m-%d"),
                        "price": 60,
                        "status": "Available",
                    },
                    {
                        "title": f"Group Session - {teacher.subject or 'General'}",
                        "location": "Online",
                        "start_hour": "16:00",
                        "end_hour": "17:00",
                        "date": (base_date + timedelta(days=3)).strftime("%Y-%m-%d"),
                        "price": 40,
                        "status": "Available",
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
                        teacher_id=teacher.id,
                        service_id=None,
                    )
                    db.add(session)
                    print(f"  Added: {session_data['title']} on {session_data['date']}")
                
                db.commit()
                print(f"  ✅ Seeded 3 sessions")
            else:
                print(f"  ⏭️  Skipping (already has sessions)")
        
        print("\n✅ Session seeding complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_sessions()
