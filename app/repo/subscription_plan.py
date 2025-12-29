"""Subscription plan repository."""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.subscription_plan import SubscriptionPlan


class SubscriptionPlanRepository:
    """Repository for subscription plan operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_active_plans(self) -> List[SubscriptionPlan]:
        """Get all active subscription plans ordered by display order."""
        return self.db.query(SubscriptionPlan).filter(
            SubscriptionPlan.is_active == True
        ).order_by(SubscriptionPlan.display_order).all()
    
    def get_all_plans(self) -> List[SubscriptionPlan]:
        """Get all subscription plans (including inactive)."""
        return self.db.query(SubscriptionPlan).order_by(
            SubscriptionPlan.display_order
        ).all()
    
    def get_plan_by_id(self, plan_id: str) -> Optional[SubscriptionPlan]:
        """Get plan by plan_id."""
        return self.db.query(SubscriptionPlan).filter(
            SubscriptionPlan.plan_id == plan_id
        ).first()
    
    def get_plan_by_pk(self, pk: int) -> Optional[SubscriptionPlan]:
        """Get plan by primary key."""
        return self.db.query(SubscriptionPlan).filter(
            SubscriptionPlan.id == pk
        ).first()
    
    def create_plan(self, plan_id: str, plan_name: str, duration_days: int, 
                    tier: str, price: int, display_order: int = 0) -> SubscriptionPlan:
        """Create a new subscription plan."""
        plan = SubscriptionPlan(
            plan_id=plan_id,
            plan_name=plan_name,
            duration_days=duration_days,
            tier=tier,
            price=price,
            display_order=display_order
        )
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan
    
    def update_plan(self, pk: int, **kwargs) -> Optional[SubscriptionPlan]:
        """Update a subscription plan."""
        plan = self.get_plan_by_pk(pk)
        if not plan:
            return None
        
        for key, value in kwargs.items():
            if hasattr(plan, key):
                setattr(plan, key, value)
        
        self.db.commit()
        self.db.refresh(plan)
        return plan
    
    def toggle_plan_status(self, pk: int) -> Optional[bool]:
        """Toggle plan active status. Returns new status."""
        plan = self.get_plan_by_pk(pk)
        if not plan:
            return None
        
        plan.is_active = not plan.is_active
        self.db.commit()
        return plan.is_active
    
    def get_next_display_order(self) -> int:
        """Get next display order number."""
        max_order = self.db.query(SubscriptionPlan).order_by(
            SubscriptionPlan.display_order.desc()
        ).first()
        return (max_order.display_order + 1) if max_order else 1
