from app.database.database import SessionLocal
from app.models.students import Student

db = SessionLocal()

student = db.query(Student).filter(Student.id == 5).first()
if student:
    print(f'Student: {student.full_name} (ID: {student.id})\n')
    
    print(f'Sessions Booked: {len(student.sessions)}')
    for sess in student.sessions:
        print(f'  - {sess.title} on {sess.date}')
        print(f'    Service: {sess.service.name if sess.service else "No service"}')
        print(f'    Documents in this session: {len(sess.documents)}')
        for doc in sess.documents:
            print(f'      - {doc.title}')
    
    print(f'\nDocuments Accessible to Student: {len(student.documents)}')
    for doc in student.documents:
        print(f'  - {doc.title}')

db.close()
