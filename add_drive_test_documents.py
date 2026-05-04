#!/usr/bin/env python3
"""
Add test documents from Google Drive to the database for preview testing.

To use:
1. Go to your Drive folder and get the file IDs for each file
2. Replace the placeholder IDs in GOOGLE_DRIVE_FILES below
3. Run: python add_drive_test_documents.py

How to get a Google Drive file ID:
  - Open the file in Google Drive
  - Copy from URL: https://drive.google.com/file/d/[FILE_ID]/view
  - The FILE_ID is the long alphanumeric string between /d/ and /view
"""

from datetime import datetime
import sys

from app.database.database import SessionLocal
from app.models.documents import Document
from app.models.teacher import Teacher
from app.models.students import Student

# Your test Google Drive file IDs
# Get these from: https://drive.google.com/drive/u/1/folders/1SzIlicfimWZvI41JhhEuqgbi7cryBUGA
GOOGLE_DRIVE_FILES = [
    {
        "title": "TD3 - Sheet 3",
        "description": "Improper and parametric integrals problem sheet",
        "drive_file_id": "1UqwgssB9Whv085qC2IGN0TGujaxuZ9-Q",
        "type": "PDF",
        "file_size": 2048576,
    },
    {
        "title": "Exceptions 2025 V2",
        "description": "Java OOP exceptions lecture PDF",
        "drive_file_id": "1ieNeoZYYHxvkq8SpgIbK5E-h1eE3qDCX",
        "type": "PDF",
        "file_size": 3145728,
    },
    {
        "title": "Examen Analyse 4 2025",
        "description": "Mathematical Analysis 4 intermediate exam PDF",
        "drive_file_id": "1kHDAEkriFeAkiSksYejBy92O4wy8RL0Z",
        "type": "PDF",
        "file_size": 1572864,
    },
]


def get_seed_teacher_id(db):
    """Pick a valid teacher_id for seed documents."""
    teacher = db.query(Teacher).order_by(Teacher.id.asc()).first()
    if not teacher:
        raise RuntimeError(
            "No teacher records found. Create at least one teacher before seeding documents."
        )
    return teacher.id


def get_or_create_seed_student(db):
    """Get a specific test student by email for seeding documents."""
    student = db.query(Student).filter(Student.email == "oa_abid@esi.dz").first()
    if student:
        return student.id, False  # Found
    
    # If student doesn't exist, we can't seed
    raise RuntimeError(
        "Student with email 'oa_abid@esi.dz' not found. Create this student first or update the email."
    )

def upsert_test_document(db, file_info, teacher_id, student_id):
    """Insert or repair a test document by title and link to student."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    preview_url = f"https://drive.google.com/file/d/{file_info['drive_file_id']}/view?usp=sharing"

    doc = db.query(Document).filter(Document.title == file_info["title"]).first()
    if doc:
        doc.description = file_info["description"]
        doc.file_path = file_info["drive_file_id"]
        doc.drive_url = preview_url
        doc.type = file_info["type"]
        doc.file_size = file_info["file_size"]
        doc.date = today
        doc.teacher_id = teacher_id
        doc.created_at = datetime.utcnow()
        action = "updated"
    else:
        doc = Document(
            title=file_info["title"],
            description=file_info["description"],
            file_path=file_info["drive_file_id"],
            drive_url=preview_url,
            type=file_info["type"],
            file_size=file_info["file_size"],
            date=today,
            teacher_id=teacher_id,
            created_at=datetime.utcnow(),
        )
        db.add(doc)
        action = "created"

    # Link to student if not already linked
    student = db.query(Student).filter(Student.id == student_id).first()
    if student and doc not in student.documents:
        student.documents.append(doc)

    return doc, action


def add_test_documents():
    """Add Google Drive test documents to the database."""
    db = SessionLocal()

    try:
        teacher_id = get_seed_teacher_id(db)
        student_id, _ = get_or_create_seed_student(db)
        
        created_count = 0
        updated_count = 0

        for file_info in GOOGLE_DRIVE_FILES:
            if file_info["drive_file_id"].startswith("1REPLACE"):
                print(
                    f"⚠️  Skipping '{file_info['title']}': Drive file ID not configured"
                )
                print(
                    "    Update GOOGLE_DRIVE_FILES with real ID from your Drive folder"
                )
                continue

            _, action = upsert_test_document(db, file_info, teacher_id, student_id)
            if action == "created":
                created_count += 1
            else:
                updated_count += 1

        if created_count > 0 or updated_count > 0:
            db.commit()
            print(
                f"✅ Seeded Google Drive documents: {created_count} created, {updated_count} updated"
            )
            print(f"   Linked to student ID: {student_id}")

            docs = db.query(Document).filter(
                Document.title.in_([f["title"] for f in GOOGLE_DRIVE_FILES])
            ).all()
            for doc in docs:
                preview_url = doc.drive_url or f"https://drive.google.com/file/d/{doc.file_path}/view?usp=sharing"
                print(f"   - {doc.title}")
                print(f"     ID: {doc.id}")
                print(f"     Drive URL: {preview_url}")
        else:
            print("❌ No documents were seeded.")

    except Exception as e:
        db.rollback()
        print(f"❌ Error adding documents: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


def list_existing_documents():
    """List all existing test documents."""
    db = SessionLocal()
    try:
        docs = db.query(Document).filter(
            Document.title.in_([f["title"] for f in GOOGLE_DRIVE_FILES])
        ).all()

        if not docs:
            print("No test documents found in database.")
            return

        print("\n📄 Existing Test Documents:")
        for doc in docs:
            print(f"   - {doc.title} (ID: {doc.id})")
            if doc.file_path:
                print(f"     Drive ID: {doc.file_path}")
            print(f"     Type: {doc.type}")
            print(f"     Size: {doc.file_size} bytes")

    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        list_existing_documents()
    else:
        print("🚀 Adding Google Drive test documents...\n")
        add_test_documents()
        print(
            "\n📝 To view these documents in the app:\n"
            "   1. Login as a student\n"
            "   2. Go to Documents section\n"
            "   3. Tap on a document to open it in Google Drive preview\n"
        )