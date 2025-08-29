"""Deletion job for auto-deleting delivered messages."""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from app.services.deletion import DeletionService

logger = logging.getLogger(__name__)


async def deletion_job_func(bot: Bot):
    """Job function to process pending deletions."""
    logger.info("Running deletion job")
    
    deletion_service = DeletionService(bot)
    await deletion_service.process_pending_deletions()
    
    logger.info("Deletion job completed")


def setup_deletion_job(scheduler: AsyncIOScheduler, bot: Bot):
    """Set up the deletion job to run every minute."""
    scheduler.add_job(
        deletion_job_func,
        'interval',
        minutes=1,
        id='deletion_job',
        args=[bot],
        replace_existing=True
    )
    
    logger.info("Deletion job scheduled to run every minute")
