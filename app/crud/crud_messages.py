from sqlalchemy import Column, DateTime, Integer, String, Boolean, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from app.database.database import  Base
from datetime import datetime,timezone
from app.models.users import User
from app.models.messages import Messages
from app.schemas.messages import MessageBase, MessageOut
from fastapi import HTTPException

def create_message(db, message: MessageBase):
    sender = db.query(User).filter(User.id == message.sender_id).first()
    receiver = db.query(User).filter(User.id == message.receiver_id).first()
    
    if not sender or not receiver:
        raise HTTPException(status_code=404, detail="Sender or Receiver not found")

    # Business Logic: 
    # - Student can only message Teacher
    # - Teacher can message Student or Teacher
    if sender.type == "Student" and receiver.type != "Teacher":
        raise HTTPException(status_code=403, detail="Students can only message Teachers")
    
    if sender.type == "Teacher" and receiver.type not in ["Student", "Teacher"]:
        raise HTTPException(status_code=403, detail="Teachers can only message Students or Teachers")

    db_message = Messages(
        sender_id=message.sender_id,
        receiver_id=message.receiver_id,
        content=message.content,
        time=message.time if message.time else None
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    # Create notification for receiver
    from app.models.notifications import Notification
    notification = Notification(
        user_id=message.receiver_id,
        message=f"{sender.full_name if hasattr(sender, 'full_name') else sender.name}: {message.content[:50]}...",
        notification_type="message"
    )
    db.add(notification)
    db.commit()
    
    return MessageOut.model_validate(db_message)
def get_messages_between_users(db, user1_id: int, user2_id: int):
    messages = db.query(Messages).filter(
        ((Messages.sender_id == user1_id) & (Messages.receiver_id == user2_id)) |
        ((Messages.sender_id == user2_id) & (Messages.receiver_id == user1_id))
    ).order_by(Messages.timestamp).all()
    return [MessageOut.model_validate(message) for message in messages]

def get_user_conversations(db, user_id: int):
    """Get all conversations with ALL messages for this user"""
    # Get all unique users that this user has either sent or received messages from
    message_records = db.query(Messages).filter(
        (Messages.sender_id == user_id) | (Messages.receiver_id == user_id)
    ).all()
    
    # Get unique peer user IDs
    peer_ids = set()
    for msg in message_records:
        if msg.sender_id == user_id:
            peer_ids.add(msg.receiver_id)
        else:
            peer_ids.add(msg.sender_id)
    
    def generate_avatar_url(name: str, user_id: int) -> str:
        """Generate avatar URL using UI Avatars service based on name"""
        # Create initials from name
        initials = "".join([w[0].upper() for w in name.split() if w])[:2]
        if not initials:
            initials = "U"
        # Use UI Avatars API to generate avatar with initials
        return f"https://ui-avatars.com/api/?name={initials}&background=random&color=fff&size=120"
    
    # Get user details for each peer
    conversations = []
    for peer_id in peer_ids:
        peer = db.query(User).filter(User.id == peer_id).first()
        if peer:
            # Get ALL messages in this conversation (sorted by timestamp)
            all_messages = db.query(Messages).filter(
                ((Messages.sender_id == user_id) & (Messages.receiver_id == peer_id)) |
                ((Messages.sender_id == peer_id) & (Messages.receiver_id == user_id))
            ).order_by(Messages.timestamp).all()
            
            # Get latest message for metadata
            latest_message = all_messages[-1] if all_messages else None
            
            peer_name = peer.full_name if hasattr(peer, 'full_name') else (peer.name if hasattr(peer, 'name') else f"User {peer.id}")
            
            # Use profile picture if available (for Teachers), otherwise generate avatar from initials
            peer_avatar = None
            if hasattr(peer, 'profile_picture') and peer.profile_picture:
                peer_avatar = peer.profile_picture
            else:
                peer_avatar = generate_avatar_url(peer_name, peer.id)
            
            conversations.append({
                "peer_id": peer.id,
                "peer_name": peer_name,
                "peer_type": peer.type if hasattr(peer, 'type') else "user",
                "peer_avatar": peer_avatar,
                "messages": [
                    {
                        "id": msg.id,
                        "sender_id": msg.sender_id,
                        "content": msg.content,
                        "timestamp": msg.timestamp,
                    }
                    for msg in all_messages
                ],
                "last_message": latest_message.content if latest_message else None,
                "last_message_at": latest_message.timestamp if latest_message else None,
            })
    
    # Sort by most recent message
    conversations.sort(
        key=lambda x: x["last_message_at"] or datetime.min if isinstance(x.get("last_message_at"), datetime) else datetime.min,
        reverse=True
    )
    
    return conversations



