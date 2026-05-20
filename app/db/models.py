from sqlalchemy import Column, Integer, String, DateTime, Float, UniqueConstraint, ForeignKey
from app.core.config import Base
from sqlalchemy.sql import func

class Ticket(Base):
    """
    SQLAlchemy model representing a support ticket.

    This model stores dev-submitted issues along with their labels metadata
    such as department and priority
    """

    __tablename__ = "tickets"
    __table_args__ = (
        UniqueConstraint('description', name = 'uq_ticket_description'),
    )
    
    id = Column(Integer, primary_key = True, index = True)
    description = Column(String, nullable = False)
    created_at = Column(DateTime(timezone = True), server_default = func.now())
    label = Column(String)
    department = Column(String)
    priority = Column(String)
    confidence = Column(Float)
    source = Column(String)
    solution = Column(String, nullable = True)
    corrected_label = Column(String, nullable = True)
    
class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key = True, index = True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable = False)
    original_label = Column(String, nullable = False)
    corrected_label = Column(String, nullable = False)
    feedback_type = Column(String, nullable = False, default = "Thumbs_Down")
    created_at = Column(DateTime(timezone = True), server_default = func.now())