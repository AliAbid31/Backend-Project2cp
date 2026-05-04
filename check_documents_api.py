#!/usr/bin/env python
from app.database.database import SessionLocal
from app.models.students import Student
from app.models.documents import Document
from app.models.services import Service

db = SessionLocal()

# Check what documents exist and their types
print("=== CHECKING DOCUMENTS FOR HIGH SCHOOL LEVEL ===\n")

student = db.query(Student).filter(Student.id == 5).first()
print(f"Student: {student.full_name}")
print(f"Educational Level: {student.educational_level}\n")

# Get all documents linked to services with High School level
documents = db.query(Document).join(
    Service, Document.service_id == Service.id
).filter(
    Service.level == "High School"
).all()

print(f"Total Documents for High School: {len(documents)}\n")

# Group by type
by_type = {}
for doc in documents:
    doc_type = doc.type or "Unknown"
    if doc_type not in by_type:
        by_type[doc_type] = []
    by_type[doc_type].append(doc)

print("Documents by Type:")
for doc_type, docs in by_type.items():
    print(f"\n{doc_type}:")
    for doc in docs:
        print(f"  - {doc.title}")

print("\n" + "="*60)
print("\nNOW CHECKING - API RESPONSE FOR /documents/suggested?level=High School\n")

# Simulate what the API should return
from app.routes.documents import get_suggested_documents

class MockQuery:
    def __init__(self):
        self.db = db

# Call the function directly
from app.routes.documents import get_suggested_documents

try:
    result = get_suggested_documents("High School", None, db, 10)
    print(f"API returned {len(result)} documents for High School")
    for doc in result:
        print(f"  - {doc.title} (Type: {doc.type})")
    
    print("\n" + "="*60)
    print("Testing with doc_type='Exercises':\n")
    
    result2 = get_suggested_documents("High School", "Exercises", db, 10)
    print(f"API returned {len(result2)} documents for High School + Exercises")
    for doc in result2:
        print(f"  - {doc.title} (Type: {doc.type})")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

db.close()
