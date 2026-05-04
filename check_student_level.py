from app.database.database import SessionLocal
from app.models.documents import Document
from app.models.students import Student
from app.models.services import Service

db = SessionLocal()

student = db.query(Student).filter(Student.id == 5).first()
print(f'Student: {student.full_name}')
print(f'Educational Level: {student.educational_level}')

print(f'\nDocuments Accessible (from association table):')
for doc in student.documents:
    service = db.query(Service).filter(Service.id == doc.service_id).first()
    print(f'  Doc ID {doc.id}: {doc.title}')
    print(f'    Type: {doc.type}')
    if service:
        print(f'    Service: {service.name} (Level: {service.level})')
    else:
        print(f'    Service: None')

db.close()
