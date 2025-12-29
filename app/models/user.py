"""User model."""
from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, DateTime, String, Text
from .base import Base


class User(Base):
    """User table to track bot users."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    tg_user_id = Column(BigInteger, unique=True, nullable=False, index=True)
    first_seen = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Subscription fields
    subscription_type = Column(String(20), default="free", nullable=False)  # 'free', 'paid'
    subscription_tier = Column(String(20), nullable=True)  # 'premium', 'plus', or None
    expiry_date = Column(BigInteger, nullable=True)  # Unix timestamp
    
    # Referral system
    referral_tokens = Column(Integer, default=3, nullable=False)  # Starting tokens
    referral_code = Column(String(10), unique=True, nullable=True, index=True)  # 8-char alphanumeric
    referred_by = Column(String(10), nullable=True)  # Referrer's code
    
    # Statistics
    total_downloads = Column(Integer, default=0, nullable=False)
    
    def __repr__(self):
        return f"<User(tg_user_id={self.tg_user_id})>"
    
    @property
    def is_subscription_active(self) -> bool:
        """Check if user has active subscription."""
        if self.subscription_type != "paid" or not self.expiry_date:
            return False
        import time
        return self.expiry_date > int(time.time())
    
    @property
    def has_plus_access(self) -> bool:
        """Check if user has Plus tier access."""
        return self.is_subscription_active and self.subscription_tier == "plus"
    
    @property
    def has_premium_access(self) -> bool:
        """Check if user has Premium or Plus tier access."""
        return self.is_subscription_active and self.subscription_tier in ("premium", "plus")

