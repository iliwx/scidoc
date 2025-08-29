"""Settings repository."""
from typing import Optional
from sqlalchemy.orm import Session
from app.models.settings import Settings


class SettingsRepository:
    """Repository for bot settings operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_settings(self) -> Settings:
        """Get bot settings, create if doesn't exist."""
        settings = self.db.query(Settings).filter(Settings.id == 1).first()
        if not settings:
            settings = Settings(id=1, next_public_number=1)
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)
        return settings
    
    def get_next_public_number(self) -> int:
        """Get and increment next public number."""
        settings = self.get_settings()
        current_number = settings.next_public_number
        settings.next_public_number += 1
        self.db.commit()
        return current_number
