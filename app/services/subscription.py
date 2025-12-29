"""Subscription service for access control and subscription management."""
import logging
import time
import random
import string
from typing import Optional, Tuple
from dataclasses import dataclass

from app.models.base import get_db
from app.models.user import User
from app.models.bundle import Bundle
from app.repo.user import UserRepository
from app.repo.download_history import DownloadHistoryRepository
from app.repo.subscription_plan import SubscriptionPlanRepository

logger = logging.getLogger(__name__)


@dataclass
class DownloadPermission:
    """Result of permission check."""
    allowed: bool
    method: Optional[str] = None  # 'subscription', 'token', 'free'
    reason: Optional[str] = None  # 'need_subscription', 'need_plus', etc.
    warning: Optional[str] = None  # Warning message to show user
    tokens_remaining: Optional[int] = None


class SubscriptionService:
    """Service for subscription and access control operations."""
    
    @staticmethod
    def can_download(user: User, bundle: Bundle) -> DownloadPermission:
        """
        Check if user can download a bundle.
        
        Returns DownloadPermission with:
        - allowed: True/False
        - method: 'free', 'subscription', 'token'
        - reason: Why denied (if applicable)
        - warning: Warning message to show
        """
        access_level = bundle.access_level or 'free'
        
        # Free documents - everyone can download
        if access_level == 'free':
            return DownloadPermission(allowed=True, method='free')
        
        # Check subscription validity
        is_subscribed = user.is_subscription_active
        
        # Plus tier access - ONLY Plus subscribers
        if access_level == 'plus':
            if is_subscribed and user.subscription_tier == 'plus':
                return DownloadPermission(allowed=True, method='subscription')
            
            if is_subscribed and user.subscription_tier == 'premium':
                return DownloadPermission(
                    allowed=False,
                    reason='need_plus',
                    warning="⭐ این محتوا فقط برای کاربران پلاس در دسترس است. اشتراک خود را ارتقا دهید."
                )
            
            return DownloadPermission(
                allowed=False,
                reason='need_plus',
                warning="⭐ برای دسترسی به این محتوا، اشتراک پلاس تهیه کنید."
            )
        
        # Premium tier access
        if access_level == 'premium':
            # Active subscription (premium or plus)
            if is_subscribed and user.subscription_tier in ('premium', 'plus'):
                return DownloadPermission(allowed=True, method='subscription')
            
            # Token redemption
            if user.referral_tokens > 0:
                warning = None
                if user.referral_tokens == 1:
                    warning = "⚠️ این آخرین توکن دانلود رایگان شماست. برای دانلود مستند جدید اشتراک تهیه کنید یا توکن دریافت کنید."
                
                return DownloadPermission(
                    allowed=True,
                    method='token',
                    warning=warning,
                    tokens_remaining=user.referral_tokens - 1
                )
            
            return DownloadPermission(
                allowed=False,
                reason='need_subscription',
                warning="💎 توکن رایگان شما تمام شده است. برای دانلود این مستند اشتراک تهیه کنید یا با دعوت دوستان توکن دریافت کنید."
            )
        
        # Unknown access level - default deny
        return DownloadPermission(allowed=False, reason='unknown')
    
    @staticmethod
    def process_download(user: User, bundle: Bundle, permission: DownloadPermission, db) -> bool:
        """
        Process a download: deduct tokens if needed, log to history.
        
        Returns True if successful.
        """
        try:
            user_repo = UserRepository(db)
            history_repo = DownloadHistoryRepository(db)
            
            # Deduct token if method is 'token'
            if permission.method == 'token':
                if user.referral_tokens <= 0:
                    return False
                user.referral_tokens -= 1
                db.commit()
                logger.info(f"Token deducted for user {user.tg_user_id}, remaining: {user.referral_tokens}")
            
            # Log download
            history_repo.log_download(
                user_id=user.tg_user_id,
                bundle_id=bundle.id,
                method=permission.method
            )
            
            # Increment total downloads
            user.total_downloads += 1
            db.commit()
            
            logger.info(f"Download logged for user {user.tg_user_id}, bundle {bundle.id}, method {permission.method}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing download: {e}")
            db.rollback()
            return False
    
    @staticmethod
    def is_redownload(user: User, bundle: Bundle, db) -> bool:
        """Check if this is a re-download (user already downloaded this bundle)."""
        history_repo = DownloadHistoryRepository(db)
        return history_repo.has_user_downloaded(user.tg_user_id, bundle.id)
    
    @staticmethod
    def activate_subscription(user: User, plan_id: str, db) -> bool:
        """Activate subscription for user based on plan."""
        try:
            plan_repo = SubscriptionPlanRepository(db)
            plan = plan_repo.get_plan_by_id(plan_id)
            
            if not plan:
                logger.error(f"Plan not found: {plan_id}")
                return False
            
            # Calculate expiry
            expiry_timestamp = int(time.time()) + (plan.duration_days * 86400)
            
            # If user already has active subscription, extend it
            if user.is_subscription_active and user.expiry_date:
                expiry_timestamp = user.expiry_date + (plan.duration_days * 86400)
            
            # Update user
            user.subscription_type = 'paid'
            user.subscription_tier = plan.tier
            user.expiry_date = expiry_timestamp
            db.commit()
            
            logger.info(f"Subscription activated for user {user.tg_user_id}: {plan.plan_name}, expires at {expiry_timestamp}")
            return True
            
        except Exception as e:
            logger.error(f"Error activating subscription: {e}")
            db.rollback()
            return False
    
    @staticmethod
    def generate_referral_code() -> str:
        """Generate a unique 8-character referral code."""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    @staticmethod
    def credit_referrer(referrer_code: str, db) -> Optional[User]:
        """Credit a referrer with a token. Returns the referrer User if successful."""
        try:
            user_repo = UserRepository(db)
            referrer = user_repo.get_user_by_referral_code(referrer_code)
            
            if not referrer:
                return None
            
            referrer.referral_tokens += 1
            db.commit()
            
            logger.info(f"Referrer {referrer.tg_user_id} credited with 1 token, total: {referrer.referral_tokens}")
            return referrer
            
        except Exception as e:
            logger.error(f"Error crediting referrer: {e}")
            db.rollback()
            return None
