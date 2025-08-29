"""User model."""
from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, DateTime
from .base import Base


class User(Base):
    """User table to track bot users."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    tg_user_id = Column(BigInteger, unique=True, nullable=False, index=True)
    first_seen = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<User(tg_user_id={self.tg_user_id})>"
