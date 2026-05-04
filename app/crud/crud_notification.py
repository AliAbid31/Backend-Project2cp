from sqlalchemy import Column, DateTime, Integer, String, Boolean, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from app.database.database import Base
from datetime import datetime,timezone
from app.models.users import User

from app.models.notifications import Notification
from sqlalchemy.orm import Session

from app.schemas.notifications import NotificationOut, NotificationBase

def create_notification(db: Session, notification: NotificationBase, user_id: int) :
    db_notification = Notification(
        user_id=user_id,
        message=notification.message,
        notification_type=notification.notification_type
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return NotificationOut.model_validate(db_notification)
def get_notifications_for_user(db: Session, user_id: int):
    notifications = db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).all()
    return [NotificationOut.model_validate(notification) for notification in notifications]
def mark_notification_as_seen(db: Session, notification_id: int, user_id: int):
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user_id
    ).first()
    
    if not notification:
        return None
    
    notification.is_seen = True
    db.commit()
    db.refresh(notification)
    return NotificationOut.model_validate(notification)

