#!/usr/bin/env python
from app.database.database import SessionLocal
from app.models.students import Student

db = SessionLocal()

print("=== FIXING STUDENT EDUCATIONAL LEVEL ===\n")

# Get the student
student = db.query(Student).filter(Student.id == 5).first()
if student:
    print(f"Current level: '{student.educational_level}'")
    student.educational_level = "High School"
    db.commit()
    print(f"Updated to: '{student.educational_level}'")
    print("✓ Student level updated successfully!")
else:
    print("Student not found")

db.close()
