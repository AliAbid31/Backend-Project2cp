from app.database.database import SessionLocal
from app.models.students import Student
from app.models.session import Session as SessionModel

db = SessionLocal()

student = db.query(Student).filter(Student.id == 5).first()
session5 = db.query(SessionModel).filter(SessionModel.id == 5).first()

print("=" * 60)
print("CHECKING SESSION 5 (Booked Subject Session)")
print("=" * 60)
print(f"\nSession 5:")
print(f"  Title: {session5.title}")
print(f"  Date: {session5.date}")
print(f"  Documents in session: {len(session5.documents)}")
for doc in session5.documents:
    print(f"    - {doc.title}")

print(f"\nStudent: {student.full_name}")
print(f"  Booked sessions: {len(student.sessions)}")
for sess in student.sessions:
    print(f"    - {sess.id}: {sess.title}")

print(f"\n  Documents accessible: {len(student.documents)}")
for doc in student.documents:
    print(f"    - {doc.title}")

# Check if session 5 is in student's booked sessions
is_booked = any(s.id == 5 for s in student.sessions)
print(f"\n  Is session 5 booked by student? {is_booked}")

# If session 5 is booked and has documents, but student doesn't see them,
# it means the linking didn't happen. We need to manually add them for session 5.
if is_booked and len(session5.documents) > 0 and len(student.documents) == 0:
    print("\n  ACTION: Session 5 has documents and is booked, but not linked to student!")
    print("  Linking documents from session 5 to student...")
    for doc in session5.documents:
        if doc not in student.documents:
            student.documents.append(doc)
    db.commit()
    print(f"  ✓ Linked {len(session5.documents)} documents")

db.close()
