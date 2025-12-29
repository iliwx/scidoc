"""Offer repository for time-limited promotions."""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.offer_backup import OfferBackup


class OfferRepository:
    """Repository for offer backup operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_offer_backup(self, bundle_id: int, original_level: str, 
                            end_time: datetime, offer_name: str = None,
                            temporary_level: str = "free") -> OfferBackup:
        """Create offer backup entry."""
        backup = OfferBackup(
            offer_name=offer_name or f"offer_{bundle_id}",
            bundle_id=bundle_id,
            original_level=original_level,
            temporary_level=temporary_level,
            start_time=datetime.utcnow(),
            end_time=end_time
        )
        self.db.add(backup)
        self.db.commit()
        self.db.refresh(backup)
        return backup
    
    def get_offer_by_id(self, offer_id: int) -> Optional[OfferBackup]:
        """Get offer by ID."""
        return self.db.query(OfferBackup).filter(OfferBackup.id == offer_id).first()
    
    def get_active_offers(self) -> List[OfferBackup]:
        """Get all active offers."""
        return self.db.query(OfferBackup).filter(
            OfferBackup.is_active == True
        ).all()
    
    def get_expired_offers(self) -> List[OfferBackup]:
        """Get offers that have expired but are still active."""
        now = datetime.utcnow()
        return self.db.query(OfferBackup).filter(
            OfferBackup.is_active == True,
            OfferBackup.end_time <= now
        ).all()
    
    def deactivate_offer(self, offer_id: int) -> bool:
        """Deactivate an offer."""
        offer = self.db.query(OfferBackup).filter(OfferBackup.id == offer_id).first()
        if not offer:
            return False
        
        offer.is_active = False
        self.db.commit()
        return True
    
    def get_bundles_by_offer(self, offer_name: str) -> List[OfferBackup]:
        """Get all bundle backups for a specific offer."""
        return self.db.query(OfferBackup).filter(
            OfferBackup.offer_name == offer_name,
            OfferBackup.is_active == True
        ).all()

