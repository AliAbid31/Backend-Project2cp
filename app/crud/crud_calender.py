from sqlalchemy.orm import Session
from app.models.session import Session as SessionModel

def get_teacher_sessions_by_date(db: Session, teacher_id: int, date_str: str):
    return db.query(SessionModel).filter(
        SessionModel.teacher_id == teacher_id,
        SessionModel.date == date_str
    ).all()
