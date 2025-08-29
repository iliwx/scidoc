"""Bundle and bundle item models."""
from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import Base


class Bundle(Base):
    """Content bundles created by admins."""
    
    __tablename__ = "bundles"
    
    id = Column(Integer, primary_key=True, index=True)
    public_number = Column(Integer, nullable=False, unique=True, index=True)
    public_number_str = Column(String(10), nullable=False, index=True)  # e.g., "0001"
    code = Column(String(50), nullable=False, unique=True, index=True)
    title = Column(String(500), nullable=False)
    created_by = Column(BigInteger, nullable=False)  # admin user ID
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationship to bundle items
    items = relationship("BundleItem", back_populates="bundle", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Bundle(public_number={self.public_number}, title='{self.title}')>"


class BundleItem(Base):
    """Individual items within a bundle."""
    
    __tablename__ = "bundle_items"
    
    id = Column(Integer, primary_key=True, index=True)
    bundle_id = Column(Integer, ForeignKey("bundles.id"), nullable=False, index=True)
    from_chat_id = Column(BigInteger, nullable=False)
    message_id = Column(Integer, nullable=False)
    media_type = Column(String(50), nullable=True)  # text, photo, video, etc.
    caption_json = Column(JSON, nullable=True)  # original caption data
    extra_json = Column(JSON, nullable=True)  # any additional metadata
    
    # Relationship to bundle
    bundle = relationship("Bundle", back_populates="items")
    
    def __repr__(self):
        return f"<BundleItem(bundle_id={self.bundle_id}, message_id={self.message_id})>"
