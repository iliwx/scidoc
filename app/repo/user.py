"""User repository."""
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import User
import random
import string


class UserRepository:
    """Repository for user operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_user(self, tg_user_id: int, generate_referral: bool = True) -> User:
        """Get existing user or create new one."""
        user = self.db.query(User).filter(User.tg_user_id == tg_user_id).first()
        if not user:
            user = User(tg_user_id=tg_user_id)
            
            # Generate unique referral code for new users
            if generate_referral:
                user.referral_code = self._generate_unique_referral_code()
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        else:
            # Update last_seen
            user.last_seen = datetime.utcnow()
            self.db.commit()
        return user
    
    def _generate_unique_referral_code(self) -> str:
        """Generate a unique 8-character referral code."""
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not self.db.query(User).filter(User.referral_code == code).first():
                return code
    
    def get_user_by_tg_id(self, tg_user_id: int) -> Optional[User]:
        """Get user by Telegram ID."""
        return self.db.query(User).filter(User.tg_user_id == tg_user_id).first()
    
    def get_user_by_referral_code(self, code: str) -> Optional[User]:
        """Get user by referral code."""
        return self.db.query(User).filter(User.referral_code == code).first()
    
    def get_all_users(self) -> List[User]:
        """Get all users."""
        return self.db.query(User).all()
    
    def get_user_count(self) -> int:
        """Get total user count."""
        return self.db.query(User).count()
    
    def get_active_users_count(self, days: int) -> int:
        """Get count of users active in last N days."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        return self.db.query(User).filter(User.last_seen >= cutoff).count()
    
    def get_referral_count(self, referral_code: str) -> int:
        """Get count of users referred by this code."""
        return self.db.query(User).filter(User.referred_by == referral_code).count()
    
    def get_subscription_counts(self) -> dict:
        """Get counts by subscription type."""
        import time
        now = int(time.time())
        
        total = self.get_user_count()
        
        # Active premium subscribers
        premium_active = self.db.query(User).filter(
            User.subscription_type == 'paid',
            User.subscription_tier == 'premium',
            User.expiry_date > now
        ).count()
        
        # Active plus subscribers
        plus_active = self.db.query(User).filter(
            User.subscription_type == 'paid',
            User.subscription_tier == 'plus',
            User.expiry_date > now
        ).count()
        
        # Expired subscriptions
        expired = self.db.query(User).filter(
            User.subscription_type == 'paid',
            User.expiry_date <= now
        ).count()
        
        # Free users (total - active subs)
        free = total - premium_active - plus_active
        
        return {
            'total': total,
            'free': free,
            'premium_active': premium_active,
            'plus_active': plus_active,
            'expired': expired
        }
    
    def get_new_users_count(self, days: int) -> int:
        """Get count of users who joined in last N days."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        return self.db.query(User).filter(User.first_seen >= cutoff).count()
    
    def search_users(self, query: str, limit: int = 10) -> List[User]:
        """Search users by ID or partial matching."""
        # Try to parse as user ID
        try:
            user_id = int(query)
            user = self.get_user_by_tg_id(user_id)
            return [user] if user else []
        except ValueError:
            pass
        
        # Search by referral code
        user = self.get_user_by_referral_code(query.upper())
        if user:
            return [user]
        
        return []
    
    def update_user(self, tg_user_id: int, **kwargs) -> Optional[User]:
        """Update user fields."""
        user = self.get_user_by_tg_id(tg_user_id)
        if not user:
            return None
        
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user

