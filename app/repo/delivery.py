"""Delivery repository."""
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.delivery import Delivery


class DeliveryRepository:
    """Repository for delivery operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_delivery(self, bundle_id: int, user_id: int, messages_json: list, 
                       delete_at: datetime) -> Delivery:
        """Create a new delivery record."""
        delivery = Delivery(
            bundle_id=bundle_id,
            user_id=user_id,
            messages_json=messages_json,
            delete_at=delete_at
        )
        self.db.add(delivery)
        self.db.commit()
        self.db.refresh(delivery)
        return delivery
    
    def get_deliveries_to_delete(self, before_time: datetime = None) -> List[Delivery]:
        """Get deliveries that need to be deleted."""
        if before_time is None:
            before_time = datetime.utcnow()
        
        return self.db.query(Delivery).filter(
            and_(
                Delivery.delete_at <= before_time,
                Delivery.deleted_at.is_(None),
                Delivery.status == "delivered"
            )
        ).all()
    
    def mark_delivery_deleted(self, delivery_id: int) -> bool:
        """Mark delivery as deleted."""
        delivery = self.db.query(Delivery).filter(Delivery.id == delivery_id).first()
        if delivery:
            delivery.deleted_at = datetime.utcnow()
            delivery.status = "deleted"
            self.db.commit()
            return True
        return False
    
    def mark_delivery_failed(self, delivery_id: int) -> bool:
        """Mark delivery as failed."""
        delivery = self.db.query(Delivery).filter(Delivery.id == delivery_id).first()
        if delivery:
            delivery.status = "failed"
            self.db.commit()
            return True
        return False
    
    def get_delivery_count(self, days: int = None) -> int:
        """Get delivery count for last N days."""
        query = self.db.query(Delivery)
        
        if days:
            cutoff = datetime.utcnow() - timedelta(days=days)
            query = query.filter(Delivery.delivered_at >= cutoff)
        
        return query.count()
    
    def get_delivery_by_id(self, delivery_id: int) -> Optional[Delivery]:
        """Get delivery by ID."""
        return self.db.query(Delivery).filter(Delivery.id == delivery_id).first()
