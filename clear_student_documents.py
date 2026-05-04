"""
Clear all student_document associations - they will be populated correctly
when students book specific sessions
"""
from app.database.database import SessionLocal
from app.models.students import Student

db = SessionLocal()

try:
    print("=" * 60)
    print("CLEARING STUDENT_DOCUMENT ASSOCIATIONS")
    print("=" * 60)
    
    students = db.query(Student).all()
    
    for student in students:
        doc_count = len(student.documents)
        if doc_count > 0:
            print(f"\n{student.full_name} (ID: {student.id}): Removing {doc_count} documents")
            student.documents.clear()
    
    db.commit()
    
    print("\n" + "=" * 60)
    print("✓ CLEARED ALL STUDENT DOCUMENT ASSOCIATIONS")
    print("=" * 60)
    print("\nStudents will now only see documents for sessions they book.")
    print("Re-book sessions for documents to be linked correctly.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
