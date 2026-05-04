#!/usr/bin/env python
from app.database.database import SessionLocal, engine
from app.models.documents import Document
from app.models.services import Service
from app.models.students import Student
from app.models.users import User

db = SessionLocal()

print("=== DEBUGGING DOCUMENTS ===\n")

# Check all students and their levels
print("STUDENTS & EDUCATIONAL LEVELS:")
students = db.query(Student).all()
for s in students:
    print(f"  Student: {s.full_name} (ID: {s.id}) | Level: '{s.educational_level}'")

print("\n" + "="*50 + "\n")

# Check all services and their levels
print("SERVICES & LEVELS:")
services = db.query(Service).all()
for s in services:
    print(f"  Service: {s.name} (ID: {s.id}) | Level: '{s.level}' | Teacher: {s.teacher_id}")

print("\n" + "="*50 + "\n")

# Check all documents and their associations
print("DOCUMENTS & SERVICE LINKS:")
documents = db.query(Document).all()
for d in documents:
    service = db.query(Service).filter(Service.id == d.service_id).first()
    service_level = service.level if service else "NO SERVICE"
    print(f"  Doc: {d.title} (ID: {d.id}) | Type: {d.type} | Service ID: {d.service_id} | Service Level: '{service_level}'")

print("\n" + "="*50 + "\n")

# Test the query logic
print("TESTING QUERY - Get documents for 'LS2':")
level = "LS2"
docs = db.query(Document).join(
    Service, Document.service_id == Service.id
).filter(
    Service.level == level
).all()
print(f"  Found {len(docs)} documents")
for d in docs:
    print(f"    - {d.filename}")
print("\nTESTING QUERY - Get documents for 'High School':")
level = "High School"
docs = db.query(Document).join(
    Service, Document.service_id == Service.id
).filter(
    Service.level == level
).all()
print(f"  Found {len(docs)} documents")
for d in docs:
    print(f"    - {d.title}")
print("\n" + "="*50 + "\n")

# Show all service levels available
print("UNIQUE SERVICE LEVELS:")
levels = db.query(Service.level).distinct().all()
for level in levels:
    print(f"  - '{level[0]}'")

db.close()
