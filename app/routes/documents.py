from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.database.database import get_db
from app.crud.crud_documents import (
    create_document,
    get_document,
    get_document_link as get_document_link_crud,
    normalize_drive_url,
    get_documents,
    get_documents_by_teacher,
    get_documents_by_type,
    get_documents_by_service,
    get_recent_documents,
    search_documents,
    delete_document,
    update_document,
    save_upload_file
)
from app.schemas.documents import DocumentCreate, DocumentOut, DocumentSearchResult
from app.database.database import SessionLocal

router = APIRouter(
    prefix="/documents",
    tags=["documents"]
)



@router.post("/upload", response_model=DocumentOut)
async def upload_document(
    title: str = Form(...),
    type: str = Form(...),
    description: Optional[str] = Form(""),
    date: str = Form(...),
    teacher_id: int = Form(...),
    service_id: Optional[int] = Form(None),
    session_id: Optional[int] = Form(None),
    drive_url: Optional[str] = Form(None),
    file: UploadFile = File(None),
    file_path: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload a new document using file path (like certificates).
    
    - **title**: Document title
    - **type**: Document type (Courses, Exercises, Homework, Other)
    - **description**: Document description
    - **date**: Date of document
    - **teacher_id**: Teacher uploading the document
    - **file_path**: Path to the file (URI or local path)
    - **service_id**: Associated service ID (optional)
    - **session_id**: Associated session ID (optional)
    """
    
    saved_path = file_path
    file_size = 0

    if file is not None:
        saved_path, file_size = await save_upload_file(file)

    if not saved_path:
        raise HTTPException(status_code=400, detail="A file or file_path is required")

    normalized_saved_path = saved_path.replace("\\", "/")

    document_data = DocumentCreate(
        title=title,
        type=type,
        description=description or "",
        date=date,
        teacher_id=teacher_id,
        drive_url=normalize_drive_url(drive_url),
        service_id=service_id,
        session_id=session_id,
    )

    return create_document(db, document_data, normalized_saved_path, file_size)


@router.get("/", response_model=list[DocumentOut])
def list_documents(
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    return get_documents(db, limit)


@router.get("/search", response_model=list[DocumentSearchResult])
def search_docs(
    q: str = Query(..., min_length=1, description="Search query"),
    type: str = Query(None, description="Filter by document type"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    return search_documents(db, q, type, limit)



@router.get("/teacher/{teacher_id}", response_model=list[DocumentOut])
def list_teacher_documents(
    teacher_id: int,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    return get_documents_by_teacher(db, teacher_id, limit)




@router.get("/service/{service_id}", response_model=list[DocumentOut])
def list_service_documents(
    service_id: int,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    return get_documents_by_service(db, service_id, limit)


@router.get("/suggested", response_model=list[DocumentSearchResult])
def get_suggested_documents(
    level: str = Query(..., description="Educational level"),
    doc_type: str = Query(None, description="Document type (Courses, Exercises, Homework, Exams)"),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get documents compatible with a specific educational level.
    Optionally filter by document type.
    Returns recent documents from services matching the educational level.
    """
    try:
        from app.models.documents import Document
        from app.models.services import Service
        
        # Build base query
        query = db.query(Document).join(
            Service, Document.service_id == Service.id
        ).filter(
            Service.level == level
        )
        
        # Optional filter by document type
        if doc_type:
            query = query.filter(Document.type == doc_type)
        
        documents = query.order_by(
            Document.created_at.desc()
        ).limit(limit).all()
        
        if not documents:
            # If no documents for this specific level, try without level filter but with type
            if doc_type:
                documents = db.query(Document).filter(
                    Document.type == doc_type
                ).order_by(
                    Document.created_at.desc()
                ).limit(limit).all()
            else:
                # Return recent documents without filters
                documents = db.query(Document).order_by(
                    Document.created_at.desc()
                ).limit(limit).all()
        
        return documents
    except Exception as e:
        print(f"Error fetching suggested documents: {e}")
        import traceback
        traceback.print_exc()
        return []


@router.get("/student/{student_id}", response_model=list[DocumentSearchResult])
def get_student_documents(
    student_id: int,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all documents accessible to a specific student
    based on their booked sessions (from student_document association table).
    
    This endpoint returns documents regardless of educational level,
    only based on what sessions/services the student has booked.
    """
    try:
        from app.models.documents import Document
        from app.models.students import Student
        
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return []
        
        # Get all documents linked to this student directly
        documents = student.documents[:limit]
        return documents
    except Exception as e:
        print(f"Error fetching student documents: {e}")
        import traceback
        traceback.print_exc()
        return []
@router.get("/{document_id}/link")
def get_document_link(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Get the Google Drive link for a specific document.
    """
    return get_document_link_crud(db, document_id)