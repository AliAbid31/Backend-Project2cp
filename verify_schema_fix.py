import requests

# Test the student profile endpoint
student_id = 1 # Assuming there's a student with ID 1
# Actually, I don't have a token, so I'll just check the schema logic by looking at the code again.
# Wait, I can use the backend directly with a script.

import os
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.students import Student
from app.schemas.students import StudentOut

db = SessionLocal()
try:
    student = db.query(Student).first()
    if student:
        out = StudentOut.from_orm(student)
        print("StudentOut data:", out.dict())
    else:
        print("No student found in DB")
finally:
    db.close()
