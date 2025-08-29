"""Scheduler setup and configuration."""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from app.config import settings

logger = logging.getLogger(__name__)


def setup_scheduler() -> AsyncIOScheduler:
    """Set up and configure the APScheduler."""
    # Use memory job store to avoid pickling issues with Bot object
    # Jobs will be re-registered on restart, which is fine for our use case
    jobstores = {
        'default': MemoryJobStore()
    }
    
    executors = {
        'default': AsyncIOExecutor()
    }
    
    job_defaults = {
        'coalesce': False,
        'max_instances': 3
    }
    
    scheduler = AsyncIOScheduler(
        jobstores=jobstores,
        executors=executors,
        job_defaults=job_defaults,
        timezone=settings.TZ
    )
    
    logger.info("Scheduler configured successfully")
    return scheduler
