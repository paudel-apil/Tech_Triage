from sqlalchemy import Column, Integer, String, DateTime, Float
from app.core.config import Base
from sqlalchemy.sql import func

class Ticket(Base):
    """
    SQLAlchemy model representing a support ticket.

    This model stores dev-submitted issues along with their labels metadata
    such as department and priority
    """

    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key = True, index = True)
    description = Column(String, nullable = False)
    created_at = Column(DateTime(timezone = True), server_default = func.now())
    label = Column(String)
    department = Column(String)
    priority = Column(String)
    confidence = Column(Float)
    source = Column(String)
    solution = Column(String, nullable = True)
    