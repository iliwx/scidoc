"""User repository."""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User


class UserRepository:
    """Repository for user operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_user(self, tg_user_id: int) -> User:
        """Get existing user or create new one."""
        user = self.db.query(User).filter(User.tg_user_id == tg_user_id).first()
        if not user:
            user = User(tg_user_id=tg_user_id)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        else:
            # Update last_seen
            user.last_seen = datetime.utcnow()
            self.db.commit()
        return user
    
    def get_user_by_tg_id(self, tg_user_id: int) -> Optional[User]:
        """Get user by Telegram ID."""
        return self.db.query(User).filter(User.tg_user_id == tg_user_id).first()
    
    def get_all_users(self) -> list[User]:
        """Get all users."""
        return self.db.query(User).all()
    
    def get_user_count(self) -> int:
        """Get total user count."""
        return self.db.query(User).count()
    
    def get_active_users_count(self, days: int) -> int:
        """Get count of users active in last N days."""
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)
        return self.db.query(User).filter(User.last_seen >= cutoff).count()
