from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.crud import crud_session
from app.schemas.session import SessionCreate, SessionOut, SessionUpdate, SessionCreateMultiple
from typing import List,Optional

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

@router.post("/book-multiple", response_model=List[SessionOut])
def book_multiple_sessions_endpoint(
    booking: SessionCreateMultiple,
    db: Session = Depends(get_db)
):
    """
    Réserve plusieurs séances à la fois pour un étudiant (Book Service).
    - Valide les dates incluses entre start_date et end_date du service.
    - Désactive les autres jours côté client.
    - Force une seule séance par jour.
    - Nombre de séances = number_of_sessions du service.
    """
    return crud_session.book_multiple_sessions(
        db=db,
        student_id=booking.student_id,
        service_id=booking.service_id,
        sessions_data=booking.sessions
    )

@router.delete("/{session_id}")
def delete_session_endpoint(session_id: int, db: Session = Depends(get_db)):
    deleted = crud_session.delete_session(db=db, session_id=session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"detail": "Session deleted successfully"}

@router.post("/create", response_model=SessionOut)
def create_session_endpoint(
    session: SessionCreate, 
    db: Session = Depends(get_db), 
):
    return crud_session.create_session(db, session)

@router.get("/", response_model=List[SessionOut])
def list_sessions(db: Session = Depends(get_db)):
    return crud_session.get_sessions(db=db)

@router.put("/{session_id}", response_model=SessionOut)
def update_session_endpoint(
    session_id: int, 
    session_update: SessionUpdate, 
    db: Session = Depends(get_db)
):
    updated_session = crud_session.update_session(
        db=db, 
        session_id=session_id, 
        session_update=session_update
    )
    if not updated_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return updated_session

@router.post("/book", response_model=SessionOut)
def create_booking(
    session: SessionCreate, 
    db: Session = Depends(get_db),
    student_id: int = Query(...),
    service_id: int = Query(...)
):
    """
    Réserve une séance de service avec validations :
    - Date comprise entre start_date et end_date du service.
    - Pas plus d'une séance par jour pour ce service/étudiant.
    """
    return crud_session.book_service_with_validation(
        db=db, 
        session_data=session, 
        student_id=student_id,
        service_id=service_id
    )


@router.get("/teacher/{teacher_id}", response_model=List[SessionOut])
def get_teacher_sessions(teacher_id: int, upcoming_only: bool = False, db: Session = Depends(get_db)):
    return crud_session.get_sessions_by_teacher(db, teacher_id, upcoming_only=upcoming_only)

@router.get("/student/{student_id}", response_model=List[SessionOut])
def get_student_sessions(student_id: int, upcoming_only: bool = False, db: Session = Depends(get_db)):
    return crud_session.get_sessions_by_student(db, student_id, upcoming_only=upcoming_only)
