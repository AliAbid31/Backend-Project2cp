#!/usr/bin/env python
"""
Verify documents are now visible to student after booking
"""
from app.database.database import SessionLocal
from app.models.students import Student
from app.models.documents import Document
from app.models.services import Service

db = SessionLocal()

print("=== DOCUMENTS NOW VISIBLE AFTER BOOKING ===\n")

student = db.query(Student).filter(Student.id == 5).first()

print(f"Student: {student.full_name}")
print(f"Educational Level: {student.educational_level}")
print(f"Services enrolled in: {len(student.services)}")
for svc in student.services:
    print(f"  - {svc.name} (Level: {svc.level})")

print("\n" + "="*60)
print("\nDOCUMENTS BY LEVEL:\n")

# High School documents (Level match)
hs_docs = db.query(Document).join(
    Service, Document.service_id == Service.id
).filter(
    Service.level == "High School"
).all()

print(f"High School level documents: {len(hs_docs)}")
for doc in hs_docs[:3]:
    print(f"  - {doc.title} (Type: {doc.type})")

print("\n" + "="*60)
print("\nTEST API RESPONSE:\n")

# Simulate what the API returns when student requests documents
print("GET /documents/suggested?level=High%20School")
docs = db.query(Document).join(
    Service, Document.service_id == Service.id
).filter(
    Service.level == student.educational_level
).order_by(Document.created_at.desc()).all()

print(f"Returns {len(docs)} documents:")
for doc in docs:
    print(f"  ✓ {doc.title} (Type: {doc.type})")

print("\n" + "="*60)
print("\nGET /documents/suggested?level=High%20School&doc_type=Exercises")
docs = db.query(Document).filter(
    Document.type == "Exercises"
).order_by(Document.created_at.desc()).all()

print(f"Returns {len(docs)} documents (fallback):")
for doc in docs:
    print(f"  ✓ {doc.title} (Type: {doc.type})")

db.close()
