"""Bundle repository."""
import secrets
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, func
from app.models.bundle import Bundle, BundleItem
from app.models.delivery import Delivery


class BundleRepository:
    """Repository for bundle operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_bundle(self, title: str, created_by: int, public_number: int, 
                       access_level: str = "premium") -> Bundle:
        """Create a new bundle with access level."""
        code = self._generate_unique_code()
        public_number_str = f"{public_number:04d}"
        
        bundle = Bundle(
            public_number=public_number,
            public_number_str=public_number_str,
            code=code,
            title=title,
            created_by=created_by,
            access_level=access_level
        )
        self.db.add(bundle)
        self.db.commit()
        self.db.refresh(bundle)
        return bundle
    
    def add_bundle_item(self, bundle_id: int, from_chat_id: int, message_id: int, 
                       media_type: str = None, caption_json: dict = None, 
                       extra_json: dict = None) -> BundleItem:
        """Add an item to a bundle."""
        item = BundleItem(
            bundle_id=bundle_id,
            from_chat_id=from_chat_id,
            message_id=message_id,
            media_type=media_type,
            caption_json=caption_json,
            extra_json=extra_json
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def get_bundle_by_code(self, code: str) -> Optional[Bundle]:
        """Get bundle by code."""
        return self.db.query(Bundle).filter(Bundle.code == code).first()
    
    def get_bundle_by_id(self, bundle_id: int) -> Optional[Bundle]:
        """Get bundle by ID."""
        return self.db.query(Bundle).filter(Bundle.id == bundle_id).first()
    
    def search_bundles(self, query: str) -> List[Bundle]:
        """Search bundles by code, number, or title."""
        search_term = f"%{query}%"
        return self.db.query(Bundle).filter(
            or_(
                Bundle.code.ilike(search_term),
                Bundle.public_number_str.ilike(search_term),
                Bundle.title.ilike(search_term)
            )
        ).order_by(desc(Bundle.created_at)).all()
    
    def get_all_bundles(self, limit: int = 50) -> List[Bundle]:
        """Get all bundles with limit."""
        return self.db.query(Bundle).order_by(desc(Bundle.created_at)).limit(limit).all()
    
    def toggle_bundle_status(self, bundle_id: int) -> bool:
        """Toggle bundle active status. Returns new status."""
        bundle = self.get_bundle_by_id(bundle_id)
        if bundle:
            bundle.is_active = not bundle.is_active
            self.db.commit()
            return bundle.is_active
        return False
    
    def get_bundle_items(self, bundle_id: int) -> List[BundleItem]:
        """Get all items for a bundle."""
        return self.db.query(BundleItem).filter(BundleItem.bundle_id == bundle_id).all()
    
    def get_bundle_count(self) -> int:
        """Get total bundle count."""
        return self.db.query(Bundle).count()
    
    def get_top_bundle_by_downloads(self, days: int = None) -> Optional[tuple]:
        """Get top bundle by downloads in last N days. Returns (bundle, download_count)."""
        query = self.db.query(Bundle, func.count(Delivery.id).label('download_count')).join(
            Delivery, Bundle.id == Delivery.bundle_id
        )
        
        if days:
            cutoff = datetime.utcnow() - timedelta(days=days)
            query = query.filter(Delivery.delivered_at >= cutoff)
        
        result = query.group_by(Bundle.id).order_by(desc('download_count')).first()
        
        if result:
            return result[0], result[1]  # bundle, count
        return None
    
    def _generate_unique_code(self) -> str:
        """Generate a unique code for the bundle."""
        while True:
            code = secrets.token_urlsafe(16)
            if not self.db.query(Bundle).filter(Bundle.code == code).first():
                return code
