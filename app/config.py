"""Configuration module for the Telegram bot."""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Bot configuration
    BOT_TOKEN: str
    ADMIN_IDS: str  # Comma-separated list of admin Telegram user IDs
    ARCHIVE_CHAT_IDS: str  # Comma-separated list of archive chat IDs
    
    # Database
    DB_URL: str = "sqlite:///data/app.db"
    
    # Timezone and logging
    TZ: str = "Asia/Tehran"
    LOG_LEVEL: str = "INFO"
    
    # Auto-deletion delay (seconds)
    AUTO_DELETE_DELAY: int = 180
    
    # Rate limiting
    FLOOD_WAIT_DELAY: int = 1
    MAX_RETRIES: int = 3
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def admin_ids_list(self) -> List[int]:
        """Parse admin IDs from comma-separated string."""
        return [int(x.strip()) for x in self.ADMIN_IDS.split(",") if x.strip()]
    
    @property
    def archive_chat_ids_list(self) -> List[int]:
        """Parse archive chat IDs from comma-separated string."""
        return [int(x.strip()) for x in self.ARCHIVE_CHAT_IDS.split(",") if x.strip()]


# Global settings instance
settings = Settings()
