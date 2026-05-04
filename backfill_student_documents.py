"""
Backfill student_document association table based on existing student_service associations
This ensures students who already booked services are now linked to the documents
"""
from app.database.database import SessionLocal
from app.models.students import Student
from app.models.services import Service
from app.models.documents import Document

db = SessionLocal()

try:
    print("=" * 60)
    print("BACKFILLING STUDENT_DOCUMENT ASSOCIATIONS")
    print("=" * 60)
    
    # Get all students
    students = db.query(Student).all()
    total_links = 0
    
    for student in students:
        print(f"\nProcessing student: {student.full_name} (ID: {student.id})")
        print(f"  Services: {len(student.services)}")
        
        # For each service the student is enrolled in
        for service in student.services:
            print(f"    Service: {service.name} - Documents: {len(service.documents)}")
            
            # Add student to all documents in that service
            for doc in service.documents:
                if doc not in student.documents:
                    student.documents.append(doc)
                    total_links += 1
                    print(f"      ✓ Added: {doc.title}")
    
    # Commit all changes
    db.commit()
    
    print("\n" + "=" * 60)
    print(f"✓ BACKFILL COMPLETE")
    print(f"  Total new document links created: {total_links}")
    print("=" * 60)
    
    # Verify
    print("\nVERIFICATION:")
    for student in db.query(Student).all():
        print(f"  {student.full_name}: {len(student.documents)} documents")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
