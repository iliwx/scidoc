"""Deletion service for auto-deleting delivered messages."""
import logging
from datetime import datetime
from typing import List
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from sqlalchemy.orm import Session

from app.models.base import get_db
from app.repo.delivery import DeliveryRepository
from app.services.delivery import DeliveryService

logger = logging.getLogger(__name__)


class DeletionService:
    """Service for auto-deleting delivered messages."""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.delivery_service = DeliveryService(bot)
    
    async def process_pending_deletions(self):
        """Process all pending message deletions."""
        db = next(get_db())
        try:
            delivery_repo = DeliveryRepository(db)
            
            # Get deliveries that need to be deleted
            deliveries = delivery_repo.get_deliveries_to_delete()
            
            logger.info(f"Processing {len(deliveries)} pending deletions")
            
            for delivery in deliveries:
                await self._delete_delivery_messages(delivery, delivery_repo)
                
                # Send ending message after deletion
                try:
                    # Get bundle code for re-download link
                    from app.repo.bundle import BundleRepository
                    bundle_repo = BundleRepository(db)
                    bundle = bundle_repo.get_bundle_by_id(delivery.bundle_id)
                    
                    if bundle:
                        await self.delivery_service.send_ending_message(
                            delivery.user_id, 
                            bundle.code
                        )
                except Exception as e:
                    logger.error(f"Failed to send ending message for delivery {delivery.id}: {e}")
            
        except Exception as e:
            logger.error(f"Error processing pending deletions: {e}")
        finally:
            db.close()
    
    async def _delete_delivery_messages(self, delivery, delivery_repo: DeliveryRepository):
        """Delete messages for a single delivery."""
        try:
            messages_json = delivery.messages_json
            deleted_count = 0
            failed_count = 0
            
            for msg_info in messages_json:
                try:
                    await self.bot.delete_message(
                        chat_id=msg_info["chat_id"],
                        message_id=msg_info["message_id"]
                    )
                    deleted_count += 1
                    
                except (TelegramBadRequest, TelegramForbiddenError) as e:
                    logger.warning(f"Failed to delete message {msg_info['message_id']}: {e}")
                    failed_count += 1
                    continue
            
            # Mark delivery as deleted
            delivery_repo.mark_delivery_deleted(delivery.id)
            
            logger.info(f"Delivery {delivery.id}: deleted {deleted_count}, failed {failed_count} messages")
            
        except Exception as e:
            logger.error(f"Error deleting messages for delivery {delivery.id}: {e}")
            delivery_repo.mark_delivery_failed(delivery.id)
