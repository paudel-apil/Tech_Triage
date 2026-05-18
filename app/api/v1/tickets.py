from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Ticket
from app.schemas.ticket import TicketCreate, SimilarTicket, TicketResponse, TicketListResponse
from app.services.ml_services import MLService
from app.services.qdrant_services import QdrantService
from app.services.llm_services import LLMService
from app.services.ml_service_dependency import get_ml_service

router = APIRouter(prefix = "/tickets", tags = ["tickets"])

@router.post("/", response_model = TicketResponse, status_code = 201)
def create_and_classify_ticket(ticket: TicketCreate, db: Session = Depends(get_db), ml: MLService = Depends(get_ml_service)):
    """
    Create and classify a new ticket
    """
    result = ml.classify(description = ticket.description,
                        sim_threshold = 0.60,
                        generate_solution = True, 
                        store = True)
    
    db_ticket = Ticket(
        description = ticket.description,
        label = result["label"],
        department = result["department"],
        priority = result["priority"],
        confidence = result["confidence"],
        source = result["source"],
        solution = result["solution"]
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)

    return TicketResponse(
        id=db_ticket.id,
        description=db_ticket.description,
        created_at=db_ticket.created_at.isoformat() if db_ticket.created_at else "",
        label=db_ticket.label,
        department=db_ticket.department,
        priority=db_ticket.priority,
        confidence=db_ticket.confidence,
        source=db_ticket.source,
        solution=db_ticket.solution,
        similar_tickets=result["similar_tickets"]
    )
        


@router.get("/", response_model = TicketListResponse)
def list_tickets(limit: int = Query(20, ge = 1, le = 100), offset: int = Query(0, ge = 0), db: Session = Depends(get_db)):
    """
    List previously classified tickets.
    """
    total = db.query(Ticket).count()
    tickets = db.query(Ticket).order_by(Ticket.id.desc()).offset(offset).limit(limit).all()
    ticket_responses = [
        TicketResponse(
            id=t.id,
            description=t.description,
            created_at=t.created_at.isoformat() if t.created_at else "",
            label=t.label,
            department=t.department,
            priority=t.priority,
            confidence=t.confidence,
            source=t.source,
            solution=t.solution,
            similar_tickets=[]   
        ) for t in tickets
    ]
    return TicketListResponse(tickets=ticket_responses, total=total)


@router.post("/search")
def search_tickets(payload: dict, ml: MLService = Depends(get_ml_service)):
    """
    Search new tickets by a free-text query
    """
    query = payload.get("query", "")
    if not query:
        raise HTTPException(status_code = 400, detail = "Query text is required")
    try:
        results = ml.search_incoming(query, limit = 10)
        return {"query": query, "results": results}
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))

@router.get("/{ticket_id}/similar")
def get_similar_tickets(ticket_id: int, limit: int = Query(5, ge = 1, le = 20), db: Session = Depends(get_db), ml: MLService = Depends(get_db)):
    """
    Return tickets similar to the specified ticket(by Qdrant point ID.)
    """
    db_ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    try:
        similar = ml.similar_to_ticket(ticket_id, limit=limit)
        return {"ticket_id": ticket_id, "similar": similar}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
