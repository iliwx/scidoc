"""Request service for handling user requests."""
import logging
from typing import List
from sqlalchemy.orm import Session

from app.models.base import get_db
from app.repo.request import RequestRepository
from app.models.request import Request

logger = logging.getLogger(__name__)


class RequestService:
    """Service for managing user requests."""
    
    def __init__(self):
        pass
    
    def submit_request(self, user_id: int, text: str) -> bool:
        """Submit a new user request."""
        db = next(get_db())
        try:
            request_repo = RequestRepository(db)
            request_repo.create_request(user_id, text)
            
            logger.info(f"New request submitted by user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error submitting request from user {user_id}: {e}")
            return False
        finally:
            db.close()
    
    def get_open_requests(self) -> List[Request]:
        """Get all open requests."""
        db = next(get_db())
        try:
            request_repo = RequestRepository(db)
            return request_repo.get_open_requests()
            
        except Exception as e:
            logger.error(f"Error getting open requests: {e}")
            return []
        finally:
            db.close()
    
    def resolve_request(self, request_id: int) -> bool:
        """Mark a request as resolved."""
        db = next(get_db())
        try:
            request_repo = RequestRepository(db)
            success = request_repo.resolve_request(request_id)
            
            if success:
                logger.info(f"Request {request_id} resolved")
            
            return success
            
        except Exception as e:
            logger.error(f"Error resolving request {request_id}: {e}")
            return False
        finally:
            db.close()
