"""Channel repository."""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.channel import MandatoryChannel


class ChannelRepository:
    """Repository for mandatory channel operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_channel(self, chat_id: int, title: str, username: str = None, 
                      join_link: str = None) -> MandatoryChannel:
        """Create a new mandatory channel."""
        channel = MandatoryChannel(
            chat_id=chat_id,
            title=title,
            username=username,
            join_link=join_link
        )
        self.db.add(channel)
        self.db.commit()
        self.db.refresh(channel)
        return channel
    
    def get_all_active_channels(self) -> List[MandatoryChannel]:
        """Get all active mandatory channels."""
        return self.db.query(MandatoryChannel).filter(
            MandatoryChannel.is_active == True
        ).all()
    
    def get_channel_by_id(self, channel_id: int) -> Optional[MandatoryChannel]:
        """Get channel by ID."""
        return self.db.query(MandatoryChannel).filter(
            MandatoryChannel.id == channel_id
        ).first()
    
    def get_channel_by_chat_id(self, chat_id: int) -> Optional[MandatoryChannel]:
        """Get channel by chat ID."""
        return self.db.query(MandatoryChannel).filter(
            MandatoryChannel.chat_id == chat_id
        ).first()
    
    def delete_channel(self, channel_id: int) -> bool:
        """Delete a channel."""
        channel = self.get_channel_by_id(channel_id)
        if channel:
            self.db.delete(channel)
            self.db.commit()
            return True
        return False
    
    def update_channel_info(self, chat_id: int, title: str, username: str = None) -> bool:
        """Update channel information."""
        channel = self.get_channel_by_chat_id(chat_id)
        if channel:
            channel.title = title
            if username:
                channel.username = username
            self.db.commit()
            return True
        return False
