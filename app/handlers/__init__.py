"""Handlers package."""
from .archive import router as archive_router
from .user import router as user_router
from .admin import router as admin_router
from .subscription import router as subscription_router
from .admin_subscription import router as admin_subscription_router

__all__ = [
    "archive_router",
    "user_router", 
    "admin_router",
    "subscription_router",
    "admin_subscription_router",
]


