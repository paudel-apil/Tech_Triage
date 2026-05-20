from pydantic import BaseModel, Field   
from typing import Optional

class TicketCreate(BaseModel):
    """
    Schema for creating a new ticket.

    This model defines the required input fields when someone submits
    a ticket via the API.
    """
    description: str
    sim_threshold: Optional[float] = Field(
        default = 0.60,
        ge = 0.0,
        le = 1.0,
        description = "Medoid similarity threshold (0.0 - 1.0). Lower = more LLM Fallback"
    )

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

class FeedbackCreate(BaseModel):
    feedback_type: str
    corrected_label: Optional[str] = None