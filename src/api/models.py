from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class TicketRequest(BaseModel):
    ticket_id: str
    user_email: str
    issue_description: str

class TicketResponse(BaseModel):
    ticket_id: str
    status: str
    resolution_message: str
    intent: Optional[str] = None
    is_confident: Optional[bool] = None
    is_safe: Optional[bool] = None
