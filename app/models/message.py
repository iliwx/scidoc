"""Message models for starting and ending messages."""
from datetime import datetime, date
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Date, Index
from .base import Base


class StartingMessage(Base):
    """Starting message shown to users."""
    
    __tablename__ = "starting_messages"
    
    id = Column(Integer, primary_key=True, default=1)
    from_chat_id = Column(BigInteger, nullable=True)
    message_id = Column(Integer, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<StartingMessage(from_chat_id={self.from_chat_id}, message_id={self.message_id})>"


class EndingMessage(Base):
    """Ending messages shown after auto-deletion."""
    
    __tablename__ = "ending_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    from_chat_id = Column(BigInteger, nullable=False)
    message_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<EndingMessage(name='{self.name}')>"


class EndingRotation(Base):
    """Track which ending messages were shown to prevent daily repeats."""
    
    __tablename__ = "ending_rotations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    ending_id = Column(Integer, nullable=False)
    date = Column(Date, default=date.today, nullable=False)
    
    def __repr__(self):
        return f"<EndingRotation(user_id={self.user_id}, ending_id={self.ending_id}, date={self.date})>"

# Create composite index for efficient rotation queries
Index("idx_ending_rotation_user_date", EndingRotation.user_id, EndingRotation.date)
