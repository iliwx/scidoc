"""Validation utilities."""
import re
from typing import Optional, Tuple


def validate_channel_link(link: str) -> bool:
    """Validate if the link is a valid Telegram channel/group link."""
    if not link:
        return False
    
    # Patterns for valid Telegram links
    patterns = [
        r'^https://t\.me/([a-zA-Z0-9_]+)$',  # Public channel: https://t.me/username
        r'^https://t\.me/\+([a-zA-Z0-9_-]+)$',  # Private invite: https://t.me/+invite
        r'^-?\d+$',  # Numeric chat ID: -1001234567890
    ]
    
    for pattern in patterns:
        if re.match(pattern, link.strip()):
            return True
    
    return False


def extract_chat_id_from_link(link: str) -> Optional[Tuple[int, str, str]]:
    """Extract chat ID and other info from Telegram link.
    
    Returns:
        Tuple of (chat_id, username, join_link) or None if invalid
    """
    if not link:
        return None
    
    link = link.strip()
    
    # Direct numeric ID
    if re.match(r'^-?\d+$', link):
        try:
            chat_id = int(link)
            return chat_id, None, None
        except ValueError:
            return None
    
    # Public channel: https://t.me/username
    match = re.match(r'^https://t\.me/([a-zA-Z0-9_]+)$', link)
    if match:
        username = match.group(1)
        # For public channels, we'll need to resolve the username to chat_id later
        # For now, return a placeholder chat_id that will be resolved by the bot
        return None, username, link
    
    # Private invite: https://t.me/+invite
    match = re.match(r'^https://t\.me/\+([a-zA-Z0-9_-]+)$', link)
    if match:
        # Private invite links need to be resolved by the bot
        return None, None, link
    
    return None


def is_valid_bundle_code(code: str) -> bool:
    """Check if bundle code format is valid."""
    if not code:
        return False
    
    # Allow alphanumeric codes with reasonable length
    return re.match(r'^[a-zA-Z0-9_-]{8,50}$', code) is not None
