"""
Clear all fake data - recreate database from scratch
"""
import os
from app.database.database import engine, Base

# Import all models so they register with Base metadata
from app.models.users import User
from app.models.teacher import Teacher
from app.models.students import Student
from app.models.parents import Parent
from app.models.session import Session
from app.models.services import Service
from app.models.quotes import Quote
from app.models.evaluation import Evaluation
from app.models.subject import Subject
from app.models.documents import Document
from app.models.certificates import Certificate
from app.models.report import Report
from app.models.messages import Messages
from app.models.notifications import Notification
from app.models.session_audit import SessionAudit
from app.models.password_reset import PasswordReset
from app.models.email_verification import EmailVerification
from app.models.admin import Admin

# Association models
from app.models.association_student_document import student_document
from app.models.association_teacher_student import teacher_student
from app.models.association_student_service import student_service
from app.models.association_student_session import student_session
from app.models.association_student_quote import student_quote
from app.models.association_teacher_subjects import teacher_subjects

print("🧹 Clearing all data and recreating fresh database...")

# Drop all tables
try:
    Base.metadata.drop_all(bind=engine)
    print("✓ All tables dropped")
except Exception as e:
    print(f"Note: {e}")

# Create all tables fresh
try:
    Base.metadata.create_all(bind=engine)
    print("✓ Fresh database created!")
    print("\n✅ SUCCESS: All fake data removed!")
    print("📊 Empty database ready for fresh data")
except Exception as e:
    print(f"❌ Error: {e}")
