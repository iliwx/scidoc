"""Mandatory channel model."""
from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime
from .base import Base


class MandatoryChannel(Base):
    """Mandatory channels that users must join."""
    
    __tablename__ = "mandatory_channels"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    username = Column(String(100), nullable=True)
    join_link = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<MandatoryChannel(title='{self.title}', chat_id={self.chat_id})>"
