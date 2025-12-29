"""Subscription plan model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from .base import Base


class SubscriptionPlan(Base):
    """Subscription plans with dynamic pricing and duration."""
    
    __tablename__ = "subscription_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(String(50), unique=True, nullable=False, index=True)  # e.g., '1m_premium'
    plan_name = Column(String(200), nullable=False)  # Persian name
    duration_days = Column(Integer, nullable=False)  # Dynamic: 15, 30, 90, etc.
    tier = Column(String(20), nullable=False)  # 'premium' or 'plus'
    price = Column(Integer, nullable=False)  # Price in Toman
    is_active = Column(Boolean, default=True, nullable=False)
    display_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<SubscriptionPlan(plan_id='{self.plan_id}', tier='{self.tier}', price={self.price})>"
