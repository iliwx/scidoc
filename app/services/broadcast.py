"""Broadcast service for sending messages to all users."""
import asyncio
import logging
from typing import Dict, Any
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from sqlalchemy.orm import Session

from app.models.base import get_db
from app.repo.user import UserRepository

logger = logging.getLogger(__name__)


class BroadcastService:
    """Service for broadcasting messages to users."""
    
    def __init__(self, bot: Bot):
        self.bot = bot
    
    def get_user_count(self) -> int:
        """Get total user count for broadcast preview."""
        db = next(get_db())
        try:
            user_repo = UserRepository(db)
            return user_repo.get_user_count()
        except Exception as e:
            logger.error(f"Error getting user count: {e}")
            return 0
        finally:
            db.close()
    
    async def send_broadcast(self, from_chat_id: int, message_id: int) -> Dict[str, int]:
        """Send broadcast message to all users.
        
        Returns:
            {"success": int, "failed": int}
        """
        db = next(get_db())
        try:
            user_repo = UserRepository(db)
            users = user_repo.get_all_users()
            
            success_count = 0
            failed_count = 0
            
            logger.info(f"Starting broadcast to {len(users)} users")
            
            # Send messages in batches to avoid rate limits
            batch_size = 30
            delay_between_batches = 1  # seconds
            
            for i in range(0, len(users), batch_size):
                batch = users[i:i + batch_size]
                
                # Process batch
                tasks = []
                for user in batch:
                    task = self._send_broadcast_message(user.tg_user_id, from_chat_id, message_id)
                    tasks.append(task)
                
                # Wait for batch to complete
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Count results
                for result in results:
                    if isinstance(result, Exception):
                        failed_count += 1
                    elif result:
                        success_count += 1
                    else:
                        failed_count += 1
                
                # Delay between batches
                if i + batch_size < len(users):
                    await asyncio.sleep(delay_between_batches)
                
                logger.info(f"Broadcast progress: {i + len(batch)}/{len(users)} users processed")
            
            logger.info(f"Broadcast completed: {success_count} success, {failed_count} failed")
            
            return {
                "success": success_count,
                "failed": failed_count
            }
            
        except Exception as e:
            logger.error(f"Error during broadcast: {e}")
            return {"success": 0, "failed": 0}
        finally:
            db.close()
    
    async def _send_broadcast_message(self, user_id: int, from_chat_id: int, message_id: int) -> bool:
        """Send broadcast message to a single user."""
        try:
            await self.bot.copy_message(
                chat_id=user_id,
                from_chat_id=from_chat_id,
                message_id=message_id
            )
            return True
            
        except (TelegramBadRequest, TelegramForbiddenError) as e:
            logger.debug(f"Failed to send broadcast to user {user_id}: {e}")
            return False
        except Exception as e:
            logger.warning(f"Unexpected error sending broadcast to user {user_id}: {e}")
            return False
