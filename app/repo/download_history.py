"""Download history repository."""
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.download_history import DownloadHistory
from app.models.bundle import Bundle


class DownloadHistoryRepository:
    """Repository for download history operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_download(self, user_id: int, bundle_id: int, method: str) -> DownloadHistory:
        """Log a download."""
        history = DownloadHistory(
            user_id=user_id,
            bundle_id=bundle_id,
            method=method
        )
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history
    
    def has_user_downloaded(self, user_id: int, bundle_id: int) -> bool:
        """Check if user has already downloaded this bundle."""
        return self.db.query(DownloadHistory).filter(
            DownloadHistory.user_id == user_id,
            DownloadHistory.bundle_id == bundle_id
        ).first() is not None
    
    def get_user_downloads(self, user_id: int, limit: int = 50) -> List[DownloadHistory]:
        """Get user's download history."""
        return self.db.query(DownloadHistory).filter(
            DownloadHistory.user_id == user_id
        ).order_by(DownloadHistory.downloaded_at.desc()).limit(limit).all()
    
    def get_download_count(self, days: Optional[int] = None) -> int:
        """Get total download count, optionally within last N days."""
        query = self.db.query(DownloadHistory)
        
        if days:
            cutoff = datetime.utcnow() - timedelta(days=days)
            query = query.filter(DownloadHistory.downloaded_at >= cutoff)
        
        return query.count()
    
    def get_top_bundles(self, limit: int = 10, days: Optional[int] = None) -> List[Tuple[Bundle, int]]:
        """Get top downloaded bundles with counts."""
        query = self.db.query(
            Bundle,
            func.count(DownloadHistory.id).label('download_count')
        ).join(
            DownloadHistory,
            DownloadHistory.bundle_id == Bundle.id
        )
        
        if days:
            cutoff = datetime.utcnow() - timedelta(days=days)
            query = query.filter(DownloadHistory.downloaded_at >= cutoff)
        
        return query.group_by(Bundle.id).order_by(
            func.count(DownloadHistory.id).desc()
        ).limit(limit).all()
    
    def get_downloads_by_method(self, days: Optional[int] = None) -> dict:
        """Get download counts grouped by method."""
        query = self.db.query(
            DownloadHistory.method,
            func.count(DownloadHistory.id)
        )
        
        if days:
            cutoff = datetime.utcnow() - timedelta(days=days)
            query = query.filter(DownloadHistory.downloaded_at >= cutoff)
        
        results = query.group_by(DownloadHistory.method).all()
        return {method: count for method, count in results}
