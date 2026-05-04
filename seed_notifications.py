"""
Seed sample notifications and messages for testing
"""
from app.database.database import SessionLocal
from app.models.users import User
from app.models.notifications import Notification
from app.models.messages import Messages
from app.models.students import Student
from app.models.teacher import Teacher
from datetime import datetime, timedelta, timezone
import random

db = SessionLocal()

try:
    # Get users
    users = db.query(User).limit(4).all()
    
    if len(users) < 2:
        print("❌ Need at least 2 users in the database")
        print("📝 Please create users first via registration")
    else:
        # Create sample notifications
        notification_messages = [
            "New message from a student",
            "Session scheduled for tomorrow",
            "Your quote has been accepted",
            "Document uploaded successfully",
            "New evaluation available",
            "Class reminder: Session starts in 1 hour",
        ]
        
        for user in users[:2]:
            for i, msg in enumerate(notification_messages[:3]):
                notif = Notification(
                    message=msg,
                    notification_type="message",
                    user_id=user.id,
                    is_seen=False,
                    created_at=datetime.now(timezone.utc) - timedelta(hours=i)
                )
                db.add(notif)
        
        db.commit()
        print(f"✅ Created sample notifications for {len(users[:2])} users")
        
        # Create sample messages between users
        if len(users) >= 2:
            for i in range(3):
                msg = Messages(
                    sender_id=users[0].id,
                    receiver_id=users[1].id,
                    content=f"Hello! This is test message {i+1}",
                    timestamp=datetime.now(timezone.utc) - timedelta(minutes=i*5)
                )
                db.add(msg)
                
                # Also add response
                msg2 = Messages(
                    sender_id=users[1].id,
                    receiver_id=users[0].id,
                    content=f"Hi! Thanks for message {i+1}",
                    timestamp=datetime.now(timezone.utc) - timedelta(minutes=i*5-2)
                )
                db.add(msg2)
            
            db.commit()
            print(f"✅ Created sample messages between users")
        
        print("\n📊 Sample data created successfully!")
        print(f"   - {len(users[:2]) * 3} notifications created")
        print(f"   - Messages created between first 2 users")
        
except Exception as e:
    db.rollback()
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
