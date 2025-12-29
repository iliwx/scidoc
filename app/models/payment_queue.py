"""Payment queue model for payment verification."""
from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text
from .base import Base


class PaymentQueue(Base):
    """Payment queue for admin verification."""
    
    __tablename__ = "payment_queue"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    plan_id = Column(String(50), nullable=False)  # References SubscriptionPlan.plan_id
    screenshot_file_id = Column(Text, nullable=False)  # Telegram file_id
    status = Column(String(20), default="pending", nullable=False)  # 'pending', 'approved', 'rejected'
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)
    processed_by = Column(String(100), nullable=True)  # Admin username who processed
    
    def __repr__(self):
        return f"<PaymentQueue(user_id={self.user_id}, plan_id='{self.plan_id}', status='{self.status}')>"
