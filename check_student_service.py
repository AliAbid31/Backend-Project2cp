#!/usr/bin/env python
"""
Check student_service association table
"""
from app.database.database import SessionLocal
from app.models.students import Student
from app.models.services import Service
from app.models.association_student_service import student_service

db = SessionLocal()

print("=== CHECKING STUDENT_SERVICE ASSOCIATION TABLE ===\n")

# Check how many entries in student_service
from sqlalchemy import text
result = db.execute(text("SELECT COUNT(*) FROM student_service"))
count = result.scalar()
print(f"Total rows in student_service table: {count}")

if count > 0:
    result = db.execute(text("SELECT * FROM student_service"))
    print("\nAll entries:")
    for row in result:
        print(f"  Student ID: {row[0]}, Service ID: {row[1]}")

print("\n" + "="*60)
print("\nSTUDENT INFO:")

# Get the student
student = db.query(Student).filter(Student.id == 5).first()
if student:
    print(f"Student: {student.full_name} (ID: {student.id})")
    print(f"Services linked to this student: {len(student.services)}")
    for svc in student.services:
        print(f"  - {svc.name} (ID: {svc.id}, Level: {svc.level})")
else:
    print("Student not found")

print("\n" + "="*60)
print("\nAVAILABLE SERVICES:")

# Get all services
services = db.query(Service).all()
print(f"Total services in database: {len(services)}")
for svc in services:
    print(f"  - {svc.name} (ID: {svc.id}, Level: {svc.level}, Teacher: {svc.teacher_id})")
    print(f"    Students enrolled: {len(svc.students)}")

db.close()
