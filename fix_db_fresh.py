"""
Fresh database reset script - use only if you want to start with a clean database
This will delete the old database and create a new one with the current schema
"""
import os
import sys
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

# Association models
from app.models.association_student_document import student_document
from app.models.association_teacher_student import teacher_student
from app.models.association_student_service import student_service
from app.models.association_student_session import student_session
from app.models.association_student_quote import student_quote

# Path to database file
db_file = "tutoratup.db"

# Check if database exists
if os.path.exists(db_file):
    print(f"🗑️  Deleting old database: {db_file}")
    try:
        os.remove(db_file)
        print("✓ Old database deleted")
    except Exception as e:
        print(f"❌ Error deleting database: {e}")
        sys.exit(1)

# Create fresh database with current schema
print("\n📦 Creating fresh database with current schema...")
try:
    Base.metadata.create_all(bind=engine)
    print("✓ Fresh database created successfully!")
    print("\n✅ Ready to use! Tables created:")
    print("  - users")
    print("  - students")
    print("  - teachers")
    print("  - email_verification")
    print("  - password_resets")
    print("  - and all other tables")
except Exception as e:
    print(f"❌ Error creating database: {e}")
    sys.exit(1)
