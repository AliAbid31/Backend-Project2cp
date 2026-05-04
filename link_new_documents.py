"""
Find documents not linked to student and link them if they belong to booked sessions
"""
from app.database.database import SessionLocal
from app.models.students import Student
from app.models.documents import Document
from app.models.services import Service
from app.models.session import Session as SessionModel

db = SessionLocal()

student_id = 5
student = db.query(Student).filter(Student.id == student_id).first()

print(f"Student: {student.full_name} (ID: {student.id})")
print(f"Booked Sessions: {len(student.sessions)}")

# Get all sessions booked by student
booked_session_ids = [s.id for s in student.sessions]
print(f"Session IDs: {booked_session_ids}")

# Find all documents linked to these sessions
docs_from_sessions = []
for session_id in booked_session_ids:
    docs = db.query(Document).filter(Document.session_id == session_id).all()
    docs_from_sessions.extend(docs)

print(f"\nDocuments in booked sessions: {len(docs_from_sessions)}")
for doc in docs_from_sessions:
    print(f"  - Doc {doc.id}: {doc.title} (Type: {doc.type})")

# Find documents from services student is enrolled in
docs_from_services = []
for service in student.services:
    docs = db.query(Document).filter(Document.service_id == service.id).all()
    docs_from_services.extend(docs)

print(f"\nDocuments in student's services: {len(docs_from_services)}")
for doc in docs_from_services:
    print(f"  - Doc {doc.id}: {doc.title} (Type: {doc.type})")

# Check which are NOT linked to student
print(f"\nStudent's currently linked documents: {len(student.documents)}")
linked_ids = [d.id for d in student.documents]
print(f"Linked IDs: {linked_ids}")

# Find unlinked documents from sessions
unlinked_from_sessions = [d for d in docs_from_sessions if d.id not in linked_ids]
print(f"\nUNLINKED documents from booked sessions: {len(unlinked_from_sessions)}")
for doc in unlinked_from_sessions:
    print(f"  - Doc {doc.id}: {doc.title} (Type: {doc.type})")
    print(f"    Linking to student...")
    student.documents.append(doc)

# Find unlinked documents from services
unlinked_from_services = [d for d in docs_from_services if d.id not in linked_ids]
print(f"\nUNLINKED documents from services: {len(unlinked_from_services)}")
for doc in unlinked_from_services:
    print(f"  - Doc {doc.id}: {doc.title} (Type: {doc.type})")
    # Don't link service documents by default, only session documents

if unlinked_from_sessions:
    db.commit()
    print(f"\n✓ Linked {len(unlinked_from_sessions)} new documents from sessions!")

# Final count
db.refresh(student)
print(f"\nFinal count - Student now has {len(student.documents)} documents")

db.close()
