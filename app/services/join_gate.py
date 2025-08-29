"""Join gate service for checking user channel memberships."""
import logging
from typing import List, Dict, Any
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from sqlalchemy.orm import Session

from app.models.base import get_db
from app.repo.channel import ChannelRepository

logger = logging.getLogger(__name__)


class JoinGateService:
    """Service for checking and managing channel join requirements."""
    
    def __init__(self, bot: Bot):
        self.bot = bot
    
    async def check_user_memberships(self, user_id: int) -> Dict[str, Any]:
        """Check if user is member of all mandatory channels.
        
        Returns:
            {
                "all_joined": bool,
                "missing_channels": List[dict],
                "channels": List[dict]  # all channels with join info
            }
        """
        db = next(get_db())
        try:
            channel_repo = ChannelRepository(db)
            channels = channel_repo.get_all_active_channels()
            
            if not channels:
                return {
                    "all_joined": True,
                    "missing_channels": [],
                    "channels": []
                }
            
            missing_channels = []
            all_channels_info = []
            
            for channel in channels:
                channel_info = {
                    "id": channel.id,
                    "title": channel.title,
                    "chat_id": channel.chat_id,
                    "join_link": channel.join_link or f"https://t.me/{channel.username}" if channel.username else None
                }
                
                all_channels_info.append(channel_info)
                
                # Skip membership check for placeholder channels (chat_id = 0)
                if channel.chat_id == 0:
                    # For private invite links, we can't check membership, so assume not joined
                    missing_channels.append(channel_info)
                    continue
                
                # Check membership
                is_member = await self._check_channel_membership(user_id, channel.chat_id)
                if not is_member:
                    missing_channels.append(channel_info)
            
            return {
                "all_joined": len(missing_channels) == 0,
                "missing_channels": missing_channels,
                "channels": all_channels_info
            }
            
        except Exception as e:
            logger.error(f"Error checking memberships for user {user_id}: {e}")
            return {
                "all_joined": False,
                "missing_channels": [],
                "channels": []
            }
        finally:
            db.close()
    
    async def _check_channel_membership(self, user_id: int, chat_id: int) -> bool:
        """Check if user is member of a specific channel."""
        try:
            logger.debug(f"Checking membership for user {user_id} in chat {chat_id}")
            member = await self.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
            
            # Consider user as member if they are not 'left' or 'kicked'
            is_member = member.status not in ['left', 'kicked']
            logger.debug(f"User {user_id} membership in {chat_id}: {member.status} -> {is_member}")
            return is_member
            
        except TelegramBadRequest as e:
            logger.warning(f"Bad request checking membership for user {user_id} in chat {chat_id}: {e}")
            # If the chat doesn't exist or bot doesn't have access, assume not a member
            return False
        except TelegramForbiddenError as e:
            logger.warning(f"Forbidden checking membership for user {user_id} in chat {chat_id}: {e}")
            # Bot might not be admin in the channel
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking membership for user {user_id} in chat {chat_id}: {e}")
            return False
    
    async def update_channel_info(self, chat_id: int) -> bool:
        """Update channel title and username from Telegram."""
        db = next(get_db())
        try:
            channel_repo = ChannelRepository(db)
            
            # Get chat info from Telegram
            chat = await self.bot.get_chat(chat_id)
            
            # Update in database
            success = channel_repo.update_channel_info(
                chat_id=chat_id,
                title=chat.title or chat.first_name or "Unknown",
                username=chat.username
            )
            
            logger.info(f"Updated channel info for {chat_id}: {chat.title}")
            return success
            
        except Exception as e:
            logger.error(f"Error updating channel info for {chat_id}: {e}")
            return False
        finally:
            db.close()
