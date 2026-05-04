from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.crud.crud_calender import get_teacher_sessions_by_date
from app.schemas.session import SessionOut
from typing import List

router = APIRouter(prefix="/api/calendar", tags=["calendar"])

@router.get("/teacher/{teacher_id}/sessions", response_model=List[SessionOut])
def get_sessions_for_date(
    teacher_id: int, 
    date: str = Query(..., description="Format YYYY-MM-DD"), 
    db: Session = Depends(get_db)
):
    return get_teacher_sessions_by_date(db, teacher_id=teacher_id, date_str=date)
