"""Main application entry point."""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import settings
from app.utils.logging import setup_logging
from app.utils.helpers import ensure_data_directory
from app.handlers import archive_router, user_router, admin_router, subscription_router, admin_subscription_router
from app.jobs import setup_scheduler, setup_deletion_job

logger = logging.getLogger(__name__)


async def main():
    """Main application function."""
    # Setup logging
    setup_logging()
    logger.info("Starting Telegram bot")
    
    # Ensure data directory exists
    ensure_data_directory()
    
    # Initialize bot and dispatcher
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    dp = Dispatcher()
    
    # Include routers (order matters - more specific first)
    dp.include_router(archive_router)
    dp.include_router(subscription_router)  # User subscription handlers
    dp.include_router(admin_subscription_router)  # Admin subscription handlers
    dp.include_router(user_router)
    dp.include_router(admin_router)
    
    # Setup scheduler
    scheduler = setup_scheduler()
    setup_deletion_job(scheduler, bot)
    
    try:
        # Start scheduler
        scheduler.start()
        logger.info("Scheduler started")
        
        # Start polling
        logger.info("Bot started successfully")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        raise
    finally:
        # Cleanup
        scheduler.shutdown()
        await bot.session.close()
        logger.info("Bot stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
