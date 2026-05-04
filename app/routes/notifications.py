from fastapi import APIRouter, Depends, HTTPException,FastAPI

from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.users import User
from app.models.parents import Parent
from app.models.notifications import Notification
from app.crud.crud_notification import create_notification, get_notifications_for_user, mark_notification_as_seen
from app.schemas.notifications import NotificationBase, NotificationOut
router= APIRouter(
    prefix="/notifications",
    tags=["notifications"],
)   

@router.post("/", response_model=NotificationOut)
def create_notification_endpoint(notification: NotificationBase, user_id: int, db: Session = Depends(get_db)):
    return create_notification(db, notification, user_id) 
@router.get("/user/{user_id}", response_model=list[NotificationOut])
def get_notifications_for_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    return get_notifications_for_user(db, user_id)

@router.get("/user/{user_id}/unseen", response_model=list[NotificationOut])
def get_unseen_notifications_endpoint(user_id: int, db: Session = Depends(get_db)):
    """Get only unseen notifications for a user"""
    notifications = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_seen == False
    ).order_by(Notification.created_at.desc()).all()
    return [NotificationOut.model_validate(n) for n in notifications]

@router.put("/{notification_id}/seen", response_model=NotificationOut)
def mark_notification_seen_endpoint(notification_id: int, user_id: int, db: Session = Depends(get_db)):
    """Mark a notification as seen"""
    from app.crud.crud_notification import mark_notification_as_seen
    result = mark_notification_as_seen(db, notification_id, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Notification not found")
    return result
