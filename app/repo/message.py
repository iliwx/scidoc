"""Message repository."""
from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.message import StartingMessage, EndingMessage, EndingRotation


class MessageRepository:
    """Repository for message operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def set_starting_message(self, from_chat_id: int, message_id: int) -> StartingMessage:
        """Set or update starting message."""
        msg = self.db.query(StartingMessage).filter(StartingMessage.id == 1).first()
        if not msg:
            msg = StartingMessage(id=1)
            self.db.add(msg)
        
        msg.from_chat_id = from_chat_id
        msg.message_id = message_id
        self.db.commit()
        self.db.refresh(msg)
        return msg
    
    def get_starting_message(self) -> Optional[StartingMessage]:
        """Get starting message."""
        return self.db.query(StartingMessage).filter(StartingMessage.id == 1).first()
    
    def create_ending_message(self, name: str, from_chat_id: int, message_id: int) -> EndingMessage:
        """Create a new ending message."""
        msg = EndingMessage(
            name=name,
            from_chat_id=from_chat_id,
            message_id=message_id
        )
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg
    
    def get_all_ending_messages(self) -> List[EndingMessage]:
        """Get all ending messages."""
        return self.db.query(EndingMessage).all()
    
    def get_ending_message_by_id(self, msg_id: int) -> Optional[EndingMessage]:
        """Get ending message by ID."""
        return self.db.query(EndingMessage).filter(EndingMessage.id == msg_id).first()
    
    def delete_ending_message(self, msg_id: int) -> bool:
        """Delete ending message."""
        msg = self.get_ending_message_by_id(msg_id)
        if msg:
            self.db.delete(msg)
            self.db.commit()
            return True
        return False
    
    def get_available_ending_messages(self, user_id: int, today: date = None) -> List[EndingMessage]:
        """Get ending messages not shown to user today."""
        if today is None:
            today = date.today()
        
        # Get all ending messages
        all_endings = self.get_all_ending_messages()
        
        # Get ending messages shown to user today
        shown_today = self.db.query(EndingRotation.ending_id).filter(
            EndingRotation.user_id == user_id,
            EndingRotation.date == today
        ).all()
        shown_ids = [row[0] for row in shown_today]
        
        # Return messages not shown today
        return [msg for msg in all_endings if msg.id not in shown_ids]
    
    def record_ending_shown(self, user_id: int, ending_id: int, today: date = None) -> EndingRotation:
        """Record that an ending message was shown to user."""
        if today is None:
            today = date.today()
        
        rotation = EndingRotation(
            user_id=user_id,
            ending_id=ending_id,
            date=today
        )
        self.db.add(rotation)
        self.db.commit()
        self.db.refresh(rotation)
        return rotation
