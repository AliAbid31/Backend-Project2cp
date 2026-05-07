from sqlalchemy.orm import Session
from app import models
from app.models.session import Session as SessionModel
from app.models.session_audit import SessionAudit
from app.models.students import Student
from app.models.services import Service
from app.schemas.session import SessionUpdate, SessionCreate
from fastapi import HTTPException
import datetime

def get_sessions(db: Session):
    return db.query(SessionModel).all()

def create_session(db: Session, session: SessionCreate):
    db_session = SessionModel(
        date=str(session.date),
        title=session.title,
        location=session.location,
        start_hour=session.start_hour,
        end_hour=session.end_hour,
        teacher_id=session.teacher_id,
        price=session.price,
        service_id=session.service_id,
        status=session.status or "Available"
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def update_session(db: Session, session_id: int, session_update: SessionUpdate):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        return None

    old_status = session.status

    update_data = session_update.model_dump(exclude_unset=True)
    
    # Update fields
    for key, value in update_data.items():
        if key != "reasons_for_cancellation": 
            setattr(session, key, value)

    # Use existing status if not provided, otherwise we'd get NULL constraint errors on refresh
    new_status = session.status or old_status

    if session_update.status or session_update.reasons_for_cancellation:
        audit_log = SessionAudit(
            session_id=session_id,
            old_status=old_status,
            new_status=new_status,
            reasons_for_cancellation=session_update.reasons_for_cancellation or "",
            change_at=datetime.datetime.utcnow()
        )
        db.add(audit_log)

    try:
        db.commit()
        db.refresh(session)
        return session
    except Exception as e:
        db.rollback()
        print(f"Update Error: {e}")
        return None

def book_service(db: Session, session_data: SessionCreate, student_id: int, teacher_id: int):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return None
    
    # If service_id is provided, also add student to service
    if hasattr(session_data, 'service_id') and session_data.service_id:
        service = db.query(Service).filter(Service.id == session_data.service_id).first()
        if service and service not in student.services:
            student.services.append(service)
    
    db_session = SessionModel(
        date=str(session_data.date),
        title=session_data.title,
        location=session_data.location,
        start_hour=session_data.start_hour,
        end_hour=session_data.end_hour,
        teacher_id=teacher_id or session_data.teacher_id,
        price=session_data.price,
        status="Booked"
    )
    
    db_session.students.append(student)
    
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    # After commit, add student to documents linked to this session
    from app.models.documents import Document
    docs = db.query(Document).filter(Document.session_id == db_session.id).all()
    for doc in docs:
        if doc not in student.documents:
            student.documents.append(doc)
    
    db.commit()
    return db_session

def book_multiple_sessions(db: Session, student_id: int, service_id: int, sessions_data: list):
    """
    Réserve plusieurs séances à la fois pour un service.
    - Nombre de sessions doit égaler le number_of_sessions du service.
    - Chaque date doit être dans la période du service.
    - Une seule session par jour autorisée.
    """
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if len(sessions_data) > service.number_of_sessions:
        raise HTTPException(
            status_code=400, 
            detail=f"Vous ne pouvez pas sélectionner plus de {service.number_of_sessions} séances."
        )
    
    if len(sessions_data) == 0:
        raise HTTPException(status_code=400, detail="Veuillez sélectionner au moins une séance.")

    booked_sessions = []
    selected_dates = set()
    
    # Add student to service (so they can see service-level documents)
    if service not in student.services:
        student.services.append(service)

    for s_data in sessions_data:
        if s_data.date < service.start_date or s_data.date > service.end_date:
            raise HTTPException(
                status_code=400, 
                detail=f"La date {s_data.date} est hors période ({service.start_date} à {service.end_date})"
            )
        
        if s_data.date in selected_dates:
            raise HTTPException(status_code=400, detail=f"Vous ne pouvez choisir qu'un seule séance pour le jour {s_data.date}")
        selected_dates.add(s_data.date)

        db_sess = SessionModel(
            date=s_data.date,
            title=s_data.title,
            location=s_data.location,
            start_hour=s_data.start_hour,
            end_hour=s_data.end_hour,
            teacher_id=service.teacher_id,
            service_id=service_id,
            price=s_data.price,
            status="Booked"
        )
        db_sess.students.append(student)
        db.add(db_sess)
        booked_sessions.append(db_sess)

    db.commit()
    
    # After commit, add student to documents linked to each session
    for session in booked_sessions:
        # Query documents explicitly for this session
        from app.models.documents import Document
        docs = db.query(Document).filter(Document.session_id == session.id).all()
        for doc in docs:
            if doc not in student.documents:
                student.documents.append(doc)
    
    db.commit()
    return booked_sessions

def book_service_with_validation(db: Session, session_data: SessionCreate, student_id: int, service_id: int):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if session_data.date < service.start_date or session_data.date > service.end_date:
        raise HTTPException(
            status_code=400, 
            detail=f"La date doit être comprise entre {service.start_date} et {service.end_date}"
        )

    existing_session = db.query(SessionModel).join(SessionModel.students).filter(
        SessionModel.service_id == service_id,
        SessionModel.date == session_data.date,
        Student.id == student_id
    ).first()
    
    if existing_session:
        raise HTTPException(status_code=400, detail="Vous avez déjà une séance réservée pour ce jour")

    # Add student to service (so they can see service-level documents)
    if service not in student.services:
        student.services.append(service)

    db_session = SessionModel(
        date=session_data.date,
        title=session_data.title,
        location=session_data.location,
        start_hour=session_data.start_hour,
        end_hour=session_data.end_hour,
        teacher_id=service.teacher_id,
        service_id=service_id,
        price=session_data.price,
        status="Booked"
    )
    
    db_session.students.append(student)
    
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    # After commit, add student to documents linked to this session
    for doc in db_session.documents:
        if doc not in student.documents:
            student.documents.append(doc)
    
    db.commit()
    return db_session


def delete_session(db: Session, session_id: int):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        return False
    db.delete(session)
    db.commit()
    return True

def get_sessions_by_teacher(db: Session, teacher_id: int, upcoming_only: bool = False):
    from datetime import datetime
    query = db.query(SessionModel).filter(SessionModel.teacher_id == teacher_id)
    
    if upcoming_only:
        current_date = datetime.now().strftime("%Y-%m-%d")
        query = query.filter(SessionModel.date >= current_date)
        
    return query.order_by(SessionModel.date, SessionModel.start_hour).all()

def get_sessions_by_student(db: Session, student_id: int, upcoming_only: bool = False):
    from app.models.students import Student
    from app.models.session import Session as SessionModel
    from datetime import datetime
    
    student = db.query(Student).filter(Student.id == student_id).first()        
    if not student:
        return []
    
    current_date = datetime.now().strftime("%Y-%m-%d") if upcoming_only else None
    
    # Filter direct sessions
    if upcoming_only:
        direct_sessions = [s for s in student.sessions if s.date >= current_date]
    else:
        direct_sessions = student.sessions
    
    service_ids = [s.id for s in student.services]
    
    if service_ids:
        query = db.query(SessionModel).filter(SessionModel.service_id.in_(service_ids))
        if upcoming_only:
            query = query.filter(SessionModel.date >= current_date)
        service_sessions = query.all()
    else:
        service_sessions = []
        
    all_sessions_dict = {s.id: s for s in direct_sessions}
    for s in service_sessions:
        all_sessions_dict[s.id] = s
        
    # Sort sessions by date and then by start hour
    sorted_sessions = sorted(list(all_sessions_dict.values()), key=lambda x: (x.date, x.start_hour))
    
    return sorted_sessions