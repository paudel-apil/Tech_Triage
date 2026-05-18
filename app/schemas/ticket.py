from pydantic import BaseModel
from typing import Optional

class TicketCreate(BaseModel):
    """
    Schema for creating a new ticket.

    This model defines the required input fields when someone submits
    a ticket via the API.
    """
    description: str

class SimilarTicket(BaseModel):
    similarity: float
    description: str
    label: Optional[str] = None
    department: Optional[str] = None
    priority: Optional[str] = None

class TicketResponse(BaseModel):
    """
    Schema representing a ticket returned by the API.
    """
    id: int
    description: str
    created_at: str
    label: str
    department: str
    priority: str
    confidence: float
    source: str
    solution: Optional[str] = None
    similar_tickets: list[SimilarTicket] = []

    class config:
        from_attributes = True

class TicketListResponse(BaseModel):
    """
    Schema for returning a list of tickets.
    """
    tickets: list[TicketResponse]
    total: int