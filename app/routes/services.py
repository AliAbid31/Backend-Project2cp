from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.crud.crud_services import create_service, get_services, delete_service
from app.schemas.services import ServiceCreate, ServiceOut
from typing import List, Optional

router = APIRouter(prefix='/api/services', tags=['services'])

@router.post('/', response_model=ServiceOut)
def create_new_service(service: ServiceCreate, db: Session = Depends(get_db)):
    return create_service(db=db, service=service)

@router.get('/', response_model=List[ServiceOut])
def read_services(
    limit: int = 100,
    teacher_id: Optional[int] = Query(None, description="Filter services by teacher ID"),
    db: Session = Depends(get_db)
):
    return get_services(db, limit=limit, teacher_id=teacher_id)

@router.delete('/{service_id}')
def delete_service_endpoint(service_id: int, db: Session = Depends(get_db)):
    success = delete_service(db, service_id)
    if not success:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"message": "Service deleted successfully"}
