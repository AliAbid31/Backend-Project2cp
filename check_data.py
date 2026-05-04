from app.database.database import SessionLocal
from app.models.users import User
from app.models.notifications import Notification
from app.models.messages import Messages

db = SessionLocal()

users = db.query(User).all()
notifications = db.query(Notification).all()
messages = db.query(Messages).all()

print(f'\n=== DATABASE STATUS ===')
print(f'Users in DB: {len(users)}')
print(f'Notifications in DB: {len(notifications)}')
print(f'Messages in DB: {len(messages)}')

if users:
    print(f'\nUsers:')
    for u in users[:5]:
        user_type = getattr(u, 'user_type', getattr(u, 'type', 'unknown'))
        print(f'  - ID: {u.id}, Type: {user_type}, Email: {getattr(u, "email", "N/A")}')

if notifications:
    print(f'\nNotifications (first 3):')
    for n in notifications[:3]:
        print(f'  - ID: {n.id}, User: {n.user_id}, Subject: {getattr(n, "subject", "N/A")}')

if messages:
    print(f'\nMessages (first 3):')
    for m in messages[:3]:
        print(f'  - ID: {m.id}, From: {m.sender_id}, To: {m.receiver_id}')
else:
    print('\n⚠️  NO DATA IN DATABASE')
    print('   Run: python seed_notifications.py')

db.close()
