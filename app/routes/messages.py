from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.users import User
from app.models.parents import Parent
from app.models.messages import Messages
from app.crud.crud_messages import create_message, get_messages_between_users, get_user_conversations
from app.schemas.messages import MessageBase, MessageOut
from fastapi import APIRouter, Depends, HTTPException,FastAPI


router= APIRouter(
    prefix="/messages",
    tags=["messages"],
)
@router.post("/", response_model=MessageOut)
def create_message_endpoint(message: MessageBase, db: Session = Depends(get_db)):
    return create_message(db, message)

@router.get("/between/{user1_id}/{user2_id}", response_model=list[MessageOut])
def get_messages_between_users_endpoint(user1_id: int, user2_id: int, db: Session = Depends(get_db)):
    return get_messages_between_users(db, user1_id, user2_id)

@router.get("/conversations/{user_id}")
def get_conversations_endpoint(user_id: int, db: Session = Depends(get_db)):
    """Get all conversations for a specific user"""
    return get_user_conversations(db, user_id)
