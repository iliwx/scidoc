"""Delivery tracking model."""
from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, DateTime, JSON, String, Index
from .base import Base


class Delivery(Base):
    """Track bundle deliveries to users and manage auto-deletion."""
    
    __tablename__ = "deliveries"
    
    id = Column(Integer, primary_key=True, index=True)
    bundle_id = Column(Integer, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    delivered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    messages_json = Column(JSON, nullable=False)  # [{"chat_id": user_id, "message_id": 123}, ...]
    delete_at = Column(DateTime, nullable=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="delivered", nullable=False)  # delivered, deleted, failed
    
    def __repr__(self):
        return f"<Delivery(bundle_id={self.bundle_id}, user_id={self.user_id}, status='{self.status}')>"

# Create index for efficient deletion job queries
Index("idx_delivery_delete_at", Delivery.delete_at)
