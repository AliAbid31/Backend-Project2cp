#!/usr/bin/env python3
"""
Check what sessions are stored in database and their date format
"""
from app.database.database import SessionLocal
from app.models.session import Session as SessionModel

def check_sessions():
    db = SessionLocal()
    
    try:
        # Get all sessions
        sessions = db.query(SessionModel).all()
        
        print(f"Total sessions in database: {len(sessions)}")
        print("\nSession details:")
        print("-" * 100)
        
        for session in sessions:
            print(f"ID: {session.id}")
            print(f"  Teacher ID: {session.teacher_id}")
            print(f"  Date (raw): {session.date}")
            print(f"  Date (type): {type(session.date)}")
            print(f"  Title: {session.title}")
            print(f"  Start Hour: {session.start_hour}")
            print(f"  End Hour: {session.end_hour}")
            print(f"  Status: {session.status}")
            print()
        
        # Now group by teacher and date like the frontend does
        print("\n\nGrouped by Teacher and Date:")
        print("-" * 100)
        
        teachers = {}
        for session in sessions:
            if session.teacher_id not in teachers:
                teachers[session.teacher_id] = {}
            
            date_str = session.date
            if date_str not in teachers[session.teacher_id]:
                teachers[session.teacher_id][date_str] = []
            
            teachers[session.teacher_id][date_str].append(session)
        
        for teacher_id, dates in teachers.items():
            print(f"\nTeacher ID: {teacher_id}")
            for date, session_list in dates.items():
                print(f"  Date: {date} ({len(session_list)} sessions)")
                for s in session_list:
                    print(f"    - {s.title} ({s.start_hour} - {s.end_hour})")
        
        # Check what format the frontend is expecting
        print("\n\nFrontend expects date key format: YYYY-MM-DD (e.g., 2026-03-30)")
        print("Checking if any sessions match '2026-03-30':")
        matching = db.query(SessionModel).filter(SessionModel.date == "2026-03-30").all()
        print(f"Matches: {len(matching)}")
        
    finally:
        db.close()

if __name__ == "__main__":
    check_sessions()
