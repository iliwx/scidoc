"""Delivery service for handling bundle delivery to users."""
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from sqlalchemy.orm import Session

from app.models.base import get_db
from app.repo.bundle import BundleRepository
from app.repo.delivery import DeliveryRepository
from app.repo.message import MessageRepository
from app.config import settings

logger = logging.getLogger(__name__)


class DeliveryService:
    """Service for delivering bundles to users."""
    
    def __init__(self, bot: Bot):
        self.bot = bot
    
    async def deliver_bundle(self, bundle_code: str, user_id: int) -> bool:
        """Deliver a bundle to user and schedule auto-deletion."""
        db = next(get_db())
        try:
            bundle_repo = BundleRepository(db)
            delivery_repo = DeliveryRepository(db)
            
            # Get bundle
            bundle = bundle_repo.get_bundle_by_code(bundle_code)
            if not bundle or not bundle.is_active:
                return False
            
            # Get bundle items
            items = bundle_repo.get_bundle_items(bundle.id)
            if not items:
                return False
            
            delivered_messages = []
            
            # Deliver each item via copyMessage
            for item in items:
                try:
                    result = await self.bot.copy_message(
                        chat_id=user_id,
                        from_chat_id=item.from_chat_id,
                        message_id=item.message_id
                    )
                    
                    delivered_messages.append({
                        "chat_id": user_id,
                        "message_id": result.message_id
                    })
                    
                    logger.info(f"Delivered item {item.id} to user {user_id}")
                    
                except (TelegramBadRequest, TelegramForbiddenError) as e:
                    logger.error(f"Failed to deliver item {item.id} to user {user_id}: {e}")
                    continue
            
            if not delivered_messages:
                return False
            
            # Create delivery record with auto-deletion schedule
            delete_at = datetime.utcnow() + timedelta(seconds=settings.AUTO_DELETE_DELAY)
            delivery_repo.create_delivery(
                bundle_id=bundle.id,
                user_id=user_id,
                messages_json=delivered_messages,
                delete_at=delete_at
            )
            
            logger.info(f"Bundle {bundle_code} delivered to user {user_id}, scheduled for deletion at {delete_at}")
            return True
            
        except Exception as e:
            logger.error(f"Error delivering bundle {bundle_code} to user {user_id}: {e}")
            return False
        finally:
            db.close()
    
    async def send_ending_message(self, user_id: int, bundle_code: str) -> bool:
        """Send a random ending message to user with re-download link."""
        db = next(get_db())
        try:
            message_repo = MessageRepository(db)
            
            # Get available ending messages (not shown today)
            available_endings = message_repo.get_available_ending_messages(user_id)
            
            if not available_endings:
                logger.warning(f"No available ending messages for user {user_id}")
                return False
            
            # Select random ending message
            import random
            selected_ending = random.choice(available_endings)
            
            # Copy the ending message
            await self.bot.copy_message(
                chat_id=user_id,
                from_chat_id=selected_ending.from_chat_id,
                message_id=selected_ending.message_id
            )
            
            # Send re-download reminder with hyperlinked text
            bot_username = (await self.bot.get_me()).username
            deep_link = f"https://t.me/{bot_username}?start={bundle_code}"
            
            reminder_text = f"برای [دانلود دوباره]({deep_link}) کلیک کنید."
            
            await self.bot.send_message(
                chat_id=user_id,
                text=reminder_text,
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
            
            # Record that this ending was shown
            message_repo.record_ending_shown(user_id, selected_ending.id)
            
            logger.info(f"Sent ending message {selected_ending.id} to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending ending message to user {user_id}: {e}")
            return False
        finally:
            db.close()
