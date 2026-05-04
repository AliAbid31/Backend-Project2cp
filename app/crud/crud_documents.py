from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import os
from datetime import datetime
from app.models.documents import Document
from app.models.teacher import Teacher
from app.models.session import Session as SessionModel
from app.models.services import Service
from app.schemas.documents import DocumentCreate, DocumentOut, DocumentSearchResult
from fastapi import HTTPException, UploadFile


UPLOAD_DIR = "uploads/documents"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


def normalize_drive_url(value: str | None) -> str | None:
    if not value:
        return None

    raw_value = value.strip()
    if not raw_value:
        return None

    if raw_value.startswith("http://") or raw_value.startswith("https://"):
        return raw_value

    if len(raw_value) >= 10 and all(ch.isalnum() or ch in "_-" for ch in raw_value):
        return f"https://drive.google.com/file/d/{raw_value}/view?usp=sharing"

    return None


async def save_upload_file(file: UploadFile) -> tuple[str, int]:
    """Save uploaded file to disk and return file path and size."""
    try:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_")
        filename = timestamp + file.filename
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        file_size = len(contents)
        return file_path, file_size
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File upload failed: {str(e)}")


def create_document(db: Session, document: DocumentCreate, file_path: str = None, file_size: int = None):
    """
    Create a new document.
    Validations: Teacher must exist. Service is optional.
    """
    
    teacher = db.query(Teacher).filter(Teacher.id == document.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    service = None
    # Only validate service if service_id is provided and not 0
    if document.service_id and document.service_id != 0:
        service = db.query(Service).filter(Service.id == document.service_id).first()
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
    
    normalized_file_path = file_path.replace("\\", "/") if file_path else None

    db_document = Document(
        title=document.title,
        type=document.type,
        description=document.description,
        date=document.date,
        file_path=normalized_file_path,
        drive_url=normalize_drive_url(document.drive_url),
        file_size=file_size,
        teacher_id=document.teacher_id,
        service_id=document.service_id,
        session_id=document.session_id,
        created_at=datetime.utcnow()
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    # Link uploaded docs to session/service students so student document lists stay in sync
    # even when docs are uploaded after the booking happened.
    needs_commit = False

    # Create notifications and associations for students in the session
    if document.session_id:
        from app.models.session import Session
        from app.models.notifications import Notification
        session = db.query(Session).filter(Session.id == document.session_id).first()
        if session and session.students:
            for student in session.students:
                if db_document not in student.documents:
                    student.documents.append(db_document)
                    needs_commit = True
                notification = Notification(
                    user_id=student.id,
                    message=f"📄 {teacher.full_name if hasattr(teacher, 'full_name') else teacher.name} uploaded {document.type}: {document.title}",
                    notification_type="document"
                )
                db.add(notification)
                needs_commit = True

    # Also associate with students who booked the service (if provided).
    if service and service.students:
        for student in service.students:
            if db_document not in student.documents:
                student.documents.append(db_document)
                needs_commit = True

    if needs_commit:
        db.commit()
    
    return db_document


def get_documents_for_student(db: Session, student_id: int, limit: int = 10):
    """Return student-visible documents from direct links, booked sessions, and booked services."""
    from app.models.students import Student

    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return []

    documents_by_id = {doc.id: doc for doc in student.documents}

    session_ids = [session.id for session in student.sessions]
    if session_ids:
        session_docs = db.query(Document).filter(Document.session_id.in_(session_ids)).all()
        for doc in session_docs:
            documents_by_id[doc.id] = doc

    service_ids = [service.id for service in student.services]
    if service_ids:
        service_docs = db.query(Document).filter(Document.service_id.in_(service_ids)).all()
        for doc in service_docs:
            documents_by_id[doc.id] = doc

    documents = list(documents_by_id.values())
    documents.sort(key=lambda d: d.created_at or datetime.min, reverse=True)
    return documents[:limit]


def get_document(db: Session, document_id: int):
    """Get a specific document by ID"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


def get_documents(db: Session, limit: int = 100):
    return db.query(Document).limit(limit).all()


def get_documents_by_teacher(db: Session, teacher_id: int, limit: int = 100):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    return db.query(Document).filter(
        Document.teacher_id == teacher_id
    ).limit(limit).all()


def get_documents_by_type(db: Session, doc_type: str, limit: int = 100):
    return db.query(Document).filter(
        Document.type == doc_type
    ).limit(limit).all()


def get_documents_by_service(db: Session, service_id: int, limit: int = 100):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    return db.query(Document).filter(
        Document.service_id == service_id
    ).limit(limit).all()


def get_recent_documents(db: Session, limit: int = 10):
    """Get recently uploaded documents"""
    return db.query(Document).order_by(
        Document.created_at.desc()
    ).limit(limit).all()


def search_documents(db: Session, query: str, doc_type: str = None, limit: int = 100):
    search_filter = or_(
        Document.title.ilike(f"%{query}%"),
        Document.description.ilike(f"%{query}%")
    )
    
    if doc_type:
        search_filter = and_(search_filter, Document.type == doc_type)
    
    return db.query(Document).filter(search_filter).limit(limit).all()


def delete_document(db: Session, document_id: int):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.file_path and os.path.exists(document.file_path):
        try:
            os.remove(document.file_path)
        except Exception as e:
            print(f"Warning: Could not delete file {document.file_path}: {str(e)}")
    
    db.delete(document)
    db.commit()
    return {"message": "Document deleted successfully"}


def update_document(db: Session, document_id: int, title: str = None, description: str = None, doc_type: str = None):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if title:
        document.title = title
    if description:
        document.description = description
    if doc_type:
        document.type = doc_type
    
    db.commit()
    db.refresh(document)
    return document
def get_document_link(db:Session,document_id:int):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {"drive_url": normalize_drive_url(document.drive_url)}
