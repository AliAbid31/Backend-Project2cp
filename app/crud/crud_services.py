from sqlalchemy.orm import Session
from app.models.services import Service
from app.models.documents import Document
from app.schemas.services import ServiceCreate

def create_service(db: Session, service: ServiceCreate):
    db_service = Service(
        name=service.name,
        category=service.category,
        description=service.description,
        level=service.level,
        price=service.price,
        start_date=service.start_date,
        end_date=service.end_date,
        number_of_sessions=service.number_of_sessions,
        duration=service.duration,
        type=service.type,
        teacher_id=service.teacher_id
    )
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

def get_services(db: Session, limit: int = 100, teacher_id: int = None):
    query = db.query(Service)
    if teacher_id is not None:
        query = query.filter(Service.teacher_id == teacher_id)
    return query.limit(limit).all()

def get_service_by_id(db: Session, service_id: int):
    return db.query(Service).filter(Service.id == service_id).first()

def delete_service(db: Session, service_id: int):
    db_service = db.query(Service).filter(Service.id == service_id).first()
    if db_service:
        # Delete all documents associated with this service first
        db.query(Document).filter(Document.service_id == service_id).delete()
        # Now delete the service
        db.delete(db_service)
        db.commit()
        return True
    return False
