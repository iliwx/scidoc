"""Statistics service for generating analytics."""
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.base import get_db
from app.repo.user import UserRepository
from app.repo.bundle import BundleRepository
from app.repo.delivery import DeliveryRepository

logger = logging.getLogger(__name__)


class StatsService:
    """Service for generating statistics and analytics."""
    
    def __init__(self):
        pass
    
    def get_weekly_stats(self) -> Dict[str, Any]:
        """Get statistics for the last 7 days."""
        return self._get_period_stats(7, "weekly")
    
    def get_monthly_stats(self) -> Dict[str, Any]:
        """Get statistics for the last 30 days."""
        return self._get_period_stats(30, "monthly")
    
    def get_total_stats(self) -> Dict[str, Any]:
        """Get all-time statistics."""
        db = next(get_db())
        try:
            user_repo = UserRepository(db)
            bundle_repo = BundleRepository(db)
            delivery_repo = DeliveryRepository(db)
            
            # Get totals
            total_downloads = delivery_repo.get_delivery_count()
            total_users = user_repo.get_user_count()
            total_bundles = bundle_repo.get_bundle_count()
            
            # Get top bundle
            top_bundle_info = bundle_repo.get_top_bundle_by_downloads()
            top_bundle_text = "هیچ دانلودی وجود ندارد"
            
            if top_bundle_info:
                bundle, count = top_bundle_info
                top_bundle_text = f"{bundle.public_number_str} - {bundle.title} ({count} دانلود)"
            
            return {
                "downloads": total_downloads,
                "total_users": total_users,
                "total_bundles": total_bundles,
                "top_bundle": top_bundle_text,
                "period": "total"
            }
            
        except Exception as e:
            logger.error(f"Error getting total stats: {e}")
            return {
                "downloads": 0,
                "total_users": 0,
                "total_bundles": 0,
                "top_bundle": "خطا در دریافت اطلاعات",
                "period": "total"
            }
        finally:
            db.close()
    
    def _get_period_stats(self, days: int, period_name: str) -> Dict[str, Any]:
        """Get statistics for a specific period."""
        db = next(get_db())
        try:
            user_repo = UserRepository(db)
            bundle_repo = BundleRepository(db)
            delivery_repo = DeliveryRepository(db)
            
            # Get period stats
            downloads = delivery_repo.get_delivery_count(days)
            active_users = user_repo.get_active_users_count(days)
            
            # Get top bundle for period
            top_bundle_info = bundle_repo.get_top_bundle_by_downloads(days)
            top_bundle_text = "هیچ دانلودی وجود ندارد"
            
            if top_bundle_info:
                bundle, count = top_bundle_info
                top_bundle_text = f"{bundle.public_number_str} - {bundle.title} ({count} دانلود)"
            
            return {
                "downloads": downloads,
                "active_users": active_users,
                "top_bundle": top_bundle_text,
                "period": period_name
            }
            
        except Exception as e:
            logger.error(f"Error getting {period_name} stats: {e}")
            return {
                "downloads": 0,
                "active_users": 0,
                "top_bundle": "خطا در دریافت اطلاعات",
                "period": period_name
            }
        finally:
            db.close()
