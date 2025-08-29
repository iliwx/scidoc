"""Bot settings model."""
from sqlalchemy import Column, Integer
from .base import Base


class Settings(Base):
    """Bot settings and state."""
    
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, default=1)
    next_public_number = Column(Integer, default=1, nullable=False)
    
    def __repr__(self):
        return f"<Settings(next_public_number={self.next_public_number})>"
