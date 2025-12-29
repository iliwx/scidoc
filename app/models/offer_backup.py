"""Offer backup model for time-limited promotions."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from .base import Base


class OfferBackup(Base):
    """Store original access levels during time-limited offers."""
    
    __tablename__ = "offer_backups"
    
    id = Column(Integer, primary_key=True, index=True)
    offer_name = Column(String(100), nullable=False)
    bundle_id = Column(Integer, nullable=False, index=True)
    original_level = Column(String(20), nullable=False)  # Original access_level
    temporary_level = Column(String(20), nullable=False)  # Temporary access_level during offer
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<OfferBackup(offer_name='{self.offer_name}', bundle_id={self.bundle_id})>"

