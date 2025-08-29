"""Request repository."""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.request import Request


class RequestRepository:
    """Repository for user request operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_request(self, user_id: int, text: str) -> Request:
        """Create a new user request."""
        request = Request(
            user_id=user_id,
            text=text
        )
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        return request
    
    def get_open_requests(self) -> List[Request]:
        """Get all open requests."""
        return self.db.query(Request).filter(
            Request.status == "open"
        ).order_by(desc(Request.created_at)).all()
    
    def get_request_by_id(self, request_id: int) -> Optional[Request]:
        """Get request by ID."""
        return self.db.query(Request).filter(Request.id == request_id).first()
    
    def resolve_request(self, request_id: int) -> bool:
        """Mark request as resolved."""
        request = self.get_request_by_id(request_id)
        if request:
            request.status = "closed"
            request.closed_at = datetime.utcnow()
            self.db.commit()
            return True
        return False
