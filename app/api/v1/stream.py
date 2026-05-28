import asyncio, json
from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from datetime import datetime

from app.db.session import get_db
from app.db.models import Ticket

router = APIRouter(prefix = "/stream", tags = ["stream"])



@router.get('/latest')
def get_latest_tickets(
    since_id: int = Query(0),
    limit: int = Query(20, le = 50),
    db: Session = Depends(get_db),):
    tickets = (
        db.query(Ticket)
        .filter(Ticket.id > since_id)
        .order_by(Ticket.id.desc())
        .limit(limit)
        .all()
    )
    return {
        "tickets": [
            {
                "id": t.id,
                "description": t.description,
                "label": t.label,
                "department": t.department,
                "priority": t.priority,
                "confidence": t.confidence,
                "source": t.source,
                "created_at": t.created_at.isoformat() if t.created_at else "",
            }
            for t in tickets
        ]
    }