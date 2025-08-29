"""Helper utilities."""
import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional


def generate_deep_link(bot_username: str, code: str) -> str:
    """Generate a deep link for a bundle."""
    return f"https://t.me/{bot_username}?start={code}"


def create_backup() -> Optional[str]:
    """Create a backup of the database and return the backup file path."""
    try:
        # Create backups directory if it doesn't exist
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d-%H%M")
        backup_filename = f"backup-{timestamp}.zip"
        backup_path = backup_dir / backup_filename
        
        # Create zip file with database
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add database file if it exists
            db_path = Path("data/app.db")
            if db_path.exists():
                zipf.write(db_path, "app.db")
            
            # Add any other important files
            # You can add more files here if needed
            
        return str(backup_path)
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating backup: {e}")
        return None


def ensure_data_directory():
    """Ensure the data directory exists for the database."""
    Path("data").mkdir(exist_ok=True)


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"


def safe_filename(filename: str) -> str:
    """Make a filename safe for the filesystem."""
    # Remove or replace unsafe characters
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 100:
        filename = filename[:100]
    
    return filename
