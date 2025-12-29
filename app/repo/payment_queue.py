"""Payment queue repository."""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.payment_queue import PaymentQueue


class PaymentQueueRepository:
    """Repository for payment queue operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_payment(self, user_id: int, plan_id: str, screenshot_file_id: str) -> PaymentQueue:
        """Create a new payment queue entry."""
        payment = PaymentQueue(
            user_id=user_id,
            plan_id=plan_id,
            screenshot_file_id=screenshot_file_id,
            status="pending"
        )
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment
    
    def get_pending_payments(self) -> List[PaymentQueue]:
        """Get all pending payments, oldest first."""
        return self.db.query(PaymentQueue).filter(
            PaymentQueue.status == "pending"
        ).order_by(PaymentQueue.submitted_at).all()
    
    def get_pending_count(self) -> int:
        """Get count of pending payments."""
        return self.db.query(PaymentQueue).filter(
            PaymentQueue.status == "pending"
        ).count()
    
    def get_payment_by_id(self, payment_id: int) -> Optional[PaymentQueue]:
        """Get payment by ID."""
        return self.db.query(PaymentQueue).filter(
            PaymentQueue.id == payment_id
        ).first()
    
    def approve_payment(self, payment_id: int, admin_username: str) -> Optional[PaymentQueue]:
        """Approve a payment."""
        payment = self.get_payment_by_id(payment_id)
        if not payment:
            return None
        
        payment.status = "approved"
        payment.processed_at = datetime.utcnow()
        payment.processed_by = admin_username
        self.db.commit()
        self.db.refresh(payment)
        return payment
    
    def reject_payment(self, payment_id: int, admin_username: str) -> Optional[PaymentQueue]:
        """Reject a payment."""
        payment = self.get_payment_by_id(payment_id)
        if not payment:
            return None
        
        payment.status = "rejected"
        payment.processed_at = datetime.utcnow()
        payment.processed_by = admin_username
        self.db.commit()
        self.db.refresh(payment)
        return payment
    
    def get_user_pending_payment(self, user_id: int) -> Optional[PaymentQueue]:
        """Check if user has a pending payment."""
        return self.db.query(PaymentQueue).filter(
            PaymentQueue.user_id == user_id,
            PaymentQueue.status == "pending"
        ).first()
    
    def get_approved_count(self, days: Optional[int] = None) -> int:
        """Get count of approved payments, optionally within last N days."""
        query = self.db.query(PaymentQueue).filter(PaymentQueue.status == "approved")
        
        if days:
            cutoff = datetime.utcnow() - timedelta(days=days)
            query = query.filter(PaymentQueue.processed_at >= cutoff)
        
        return query.count()
    
    def get_total_revenue(self, days: Optional[int] = None) -> int:
        """Get total revenue from approved payments."""
        from app.models.subscription_plan import SubscriptionPlan
        from datetime import timedelta
        
        query = self.db.query(func.sum(SubscriptionPlan.price)).join(
            PaymentQueue,
            PaymentQueue.plan_id == SubscriptionPlan.plan_id
        ).filter(PaymentQueue.status == "approved")
        
        if days:
            cutoff = datetime.utcnow() - timedelta(days=days)
            query = query.filter(PaymentQueue.processed_at >= cutoff)
        
        result = query.scalar()
        return result or 0


from datetime import timedelta
