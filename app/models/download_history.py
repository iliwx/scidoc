"""Download history model for analytics."""
from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Index
from .base import Base


class DownloadHistory(Base):
    """Track download history for analytics and re-download detection."""
    
    __tablename__ = "download_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    bundle_id = Column(Integer, nullable=False, index=True)
    downloaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    method = Column(String(20), nullable=False)  # 'subscription', 'token', 'free'
    
    def __repr__(self):
        return f"<DownloadHistory(user_id={self.user_id}, bundle_id={self.bundle_id}, method='{self.method}')>"


# Create composite index for efficient user+bundle queries
Index("idx_download_history_user_bundle", DownloadHistory.user_id, DownloadHistory.bundle_id)
