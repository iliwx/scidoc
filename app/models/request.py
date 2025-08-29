"""User request model."""
from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, Text, String, DateTime
from .base import Base


class Request(Base):
    """User requests submitted to admins."""
    
    __tablename__ = "requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    text = Column(Text, nullable=False)
    status = Column(String(20), default="open", nullable=False)  # open, closed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    closed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Request(id={self.id}, user_id={self.user_id}, status='{self.status}')>"
