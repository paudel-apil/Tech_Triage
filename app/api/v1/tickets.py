"""
FastAPI router for ticket lifestyle management. 

This module exposes REST APIs for:
- ticket creation & classification
- feedback collection
- ticket search
- similarity retrieval
- analytics dashboard
- trend analysis
"""

import time
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from qdrant_client.http import models as qmodels
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, case, and_, text
from app.db.session import get_db
from app.db.models import Ticket, Feedback
from app.schemas.ticket import TicketCreate, SimilarTicket, TicketResponse, TicketListResponse, FeedbackCreate
from app.services.ml_services import MLService
from app.pipeline.gen_embeddings import encode_single
from app.services.qdrant_services import QdrantService
from app.services.llm_services import LLMService
from app.services.ml_service_dependency import get_ml_service

router = APIRouter(prefix = "/tickets", tags = ["tickets"])

def find_or_create_ticket(db: Session, description: str, classification: dict):
    """
    Idempotent ticket creation logic. 

    If a ticket with the same description exists within the last hour:
    - update its classification
    - avoid duplication,
    otherwise create a new ticket record
    """
    cutoff = datetime.utcnow() - timedelta(minutes = 60)
    existing = (
        db.query(Ticket)
        .filter(
            Ticket.description == description,
            Ticket.created_at >= cutoff
        )
        .order_by(Ticket.created_at.desc())
        .first()
    )

    if existing:
        existing.label = classification["label"]
        existing.department = classification["department"]
        existing.priority = classification["priority"]
        existing.confidence = classification["confidence"]
        existing.source = classification["source"]
        existing.solution = classification.get("solution")
        db.commit()
        db.refresh(existing)
        return existing, False
    else:
        db_ticket = Ticket(
            description = description,
            label = classification["label"],
            department=classification["department"],
            priority=classification["priority"],
            confidence=classification["confidence"],
            source=classification["source"],
            solution=classification.get("solution"),
        )
        db.add(db_ticket)
        db.commit()
        db.refresh(db_ticket)
        return db_ticket, True


@router.post("/", response_model=TicketResponse, status_code=201)
def create_and_classify_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db),
    ml: MLService = Depends(get_ml_service)
):
    """
    Create and classify a support ticket. 

    Full pipeline: Generate embeddings -> run ML classification -> Query similar tickets ->
    store in PostgreSQL and Qdrant -> return enriched response.
    """
    result = ml.classify(
        description=ticket.description,
        sim_threshold=ticket.sim_threshold,
        generate_solution=True,
        store=False 
    )

    db_ticket, is_new = find_or_create_ticket(db, ticket.description, result)

    emb = encode_single(ticket.description, ml.embedder)
    ml.qdrant.client.upsert(
        collection_name=ml.qdrant.incoming_collection,
        points=[
            qmodels.PointStruct(
                id=db_ticket.id,         
                vector=emb[0].tolist(),
                payload={
                    "description": ticket.description,
                    "assigned_label": result["label"],
                    "department": result["department"],
                    "priority": result["priority"],
                    "source": result["source"],
                    "confidence": result["confidence"],
                    "classified_at": db_ticket.created_at.isoformat() if db_ticket.created_at else datetime.utcnow().isoformat()
                }
            )
        ]
    )

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
        similar_tickets=result.get("similar_tickets", [])
    )
        

@router.post("/{ticket_id}/feedback", status_code=201)
def submit_feedback(
    ticket_id: int,
    feedback: FeedbackCreate,
    db: Session = Depends(get_db)
):
    """
    Collect user feedback for classification correction.
    Supports thumbs up/down validation, manual correction
    """
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    original_label = ticket.label        

    entry = Feedback(
        ticket_id=ticket_id,
        original_label=original_label,
        corrected_label=feedback.corrected_label if feedback.feedback_type == "thumbs_down" else None,
        feedback_type=feedback.feedback_type
    )
    db.add(entry)

    if feedback.feedback_type == "thumbs_down" and feedback.corrected_label:
        ticket.corrected_label = feedback.corrected_label
        ticket.label = feedback.corrected_label          
        print(f"Ticket {ticket_id}: label corrected from '{original_label}' to '{feedback.corrected_label}'")

    db.commit()
    return {"status": "ok", "original_label": original_label, "new_label": ticket.label}


@router.get("/", response_model = TicketListResponse)
def list_tickets(limit: int = Query(20, ge = 1, le = 100), 
                 offset: int = Query(0, ge = 0), 
                 db: Session = Depends(get_db),
                 department: Optional[str] = Query(None, description = "Filter by department name")):
    """
    List previously classified tickets.
    """
    q = db.query(Ticket)
    if department:
        q = q.filter(Ticket.department == department)
    
    total = q.count()
    tickets = q.order_by(Ticket.id.desc()).offset(offset).limit(limit).all()

    return TicketListResponse(
        tickets = [
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
        ],
        total = total,
    )


@router.get("/departments", tags = ["tickets"])
def list_departments(db: Session = Depends(get_db)):
    """
    Return all distinct department names present in the DB.
    """
    dept_rows = db.query(distinct(Ticket.department)).all()
    departments = [row[0] for row in dept_rows if row[0]]
    departments = ["Uncategorised" if d.lower() == "uncategorized" else d for d in departments]
    departments = sorted(set(departments))
    return {"departments": departments}

_stats_cache = {"data": None, "ts": 0}      # Cached system stats to reduce DB load.

@router.get("/stats", tags=["tickets"])
def get_stats(db: Session = Depends(get_db)):
    """
    Compute and cache system-wide ticket statistics. 

    Includes: totals, priority breakdown, top labels, source distribution, 
    confidence metrics and department load
    """
    global _stats_cache
    now = time.time()

    if _stats_cache["data"] is not None and (now - _stats_cache["ts"]) < 60:
        return _stats_cache["data"]

    total = db.query(func.count(Ticket.id)).scalar() or 0

    priority_rows = (
        db.query(Ticket.priority, func.count(Ticket.id))
        .group_by(Ticket.priority)
        .all()
    )
    priority_breakdown = {row[0]: row[1] for row in priority_rows}

    label_rows = (
        db.query(Ticket.label, func.count(Ticket.id).label("cnt"))
        .group_by(Ticket.label)
        .order_by(func.count(Ticket.id).desc())
        .limit(5)
        .all()
    )
    top_labels = [{"label": r[0], "count": r[1]} for r in label_rows]

    source_rows = (
        db.query(Ticket.source, func.count(Ticket.id))
        .group_by(Ticket.source)
        .all()
    )
    source_breakdown = {row[0]: row[1] for row in source_rows}

    avg_conf = db.query(func.avg(Ticket.confidence)).scalar()
    avg_confidence = round(float(avg_conf), 4) if avg_conf else 0.0

    dept_rows = (
        db.query(Ticket.department, func.count(Ticket.id).label("cnt"))
        .filter(Ticket.department.isnot(None))
        .group_by(Ticket.department)
        .order_by(func.count(Ticket.id).desc())
        .all()
    )
    department_breakdown = [{"department": r[0], "count": r[1]} for r in dept_rows]

    result = {
        "total": total,
        "priority_breakdown": priority_breakdown,
        "top_labels": top_labels,
        "source_breakdown": source_breakdown,
        "avg_confidence": avg_confidence,
        "department_breakdown": department_breakdown,
    }

    _stats_cache["data"] = result
    _stats_cache["ts"] = now
    return result


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
def get_similar_tickets(ticket_id: int, limit: int = Query(5, ge = 1, le = 20), db: Session = Depends(get_db), ml: MLService = Depends(get_ml_service)):
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


# Trend Analytics Endpoints

@router.get("/trends/accelerating")
def accelerating_categories(db: Session = Depends(get_db)):
    """
    Detect categories with rising ticket volume.
    """
    now = datetime.utcnow()
    this_start = now - timedelta(days = 7)
    last_start = now - timedelta(days = 14)
    last_end = now - timedelta(days = 7)

    this_week = (
        db.query(Ticket.label, func.count(Ticket.id))
        .filter(Ticket.created_at >= this_start)
        .group_by(Ticket.label)
        .all()
    )

    last_week = (
        db.query(Ticket.label, func.count(Ticket.id))
        .filter(Ticket.created_at >= last_start, Ticket.created_at < last_end)
        .group_by(Ticket.label)
        .all()
    )

    this_dict = {row[0]: row[1] for row in this_week}
    last_dict = {row[0]: row[1] for row in last_week}

    result = []
    for label, this_count in sorted(this_dict.items(), key = lambda x: x[1], reverse = True)[:20]:
        last_count = last_dict.get(label, 0)
        if last_count > 0:
            change = round(((this_count - last_count) / last_count) * 100, 1)
        else:
            change = 100.0 if this_count > 0 else 0.0
        result.append({
            "label": label,
            "this_week": this_count,
            "last_week": last_count,
            "change_pct": change
        })

    for label, last_count in last_dict.items():
        if label not in this_dict:
            result.append({
                "label": label,
                "this_week": 0,
                "last_week": last_count,
                "change_pct": -100.0
            })

    return {"categories": result}


@router.get("/trends/priority-timeline")
def priority_timeline(db: Session = Depends(get_db), days: int = 7, granularity: str = "hour"):
    """
    Time-based priority distribution analysis.
    """
    now = datetime.utcnow()
    start = now - timedelta(days = days)

    trunc = text("date_trunc(:gran, created_at)") if granularity == "hour" else func.date(func.date_trunc('day', Ticket.created_at))
    if granularity == "hour":
        trunc = func.date_trunc('hour', Ticket.created_at)
    else:
        trunc = func.date(func.date_trunc('day', Ticket.created_at))

    rows = (
        db.query(trunc.label("ts"), Ticket.priority, func.count(Ticket.id))
        .filter(Ticket.created_at >= start)
        .group_by("ts", Ticket.priority)
        .order_by("ts")
        .all()
    )
    return {
        "timeline": [
            {"timestamps": row[0].isoformat(), "priority": row[1], "count": row[2]}
            for row in rows
        ]
    }

@router.get("/trends/fallback-rate")
def fallback_rate(db: Session = Depends(get_db), days: int = 14):
    """
    Measure how often LLM fallback is triggered.
    """
    now = datetime.utcnow()
    start = now - timedelta(days = days)

    total_per_day = (
        db.query(func.date(Ticket.created_at).label("day"), func.count(Ticket.id))
        .filter(Ticket.created_at >= start)
        .group_by("day")
        .all()
    )
    llm_per_day = (
        db.query(func.date(Ticket.created_at).label("day"), func.count(Ticket.id))
        .filter(Ticket.created_at >= start, Ticket.source == "llm_fallback")
        .group_by("day")
        .all()
    )

    total_dict = {row[0]: row[1] for row in total_per_day}
    llm_dict = {row[0]: row[1] for row in llm_per_day}

    timeline = []
    for day, total in sorted(total_dict.items()):
        llm = llm_dict.get(day, 0)
        rate = round(llm / total, 4) if total > 0 else 0.0
        timeline.append({"date": day.isoformat(), "rate": rate})

    return {"timeline": timeline}


@router.get("/trends/department-load")
def department_load(db: Session = Depends(get_db), days: int = 14):
    """
    Track department-wise ticket load over time
    """
    now = datetime.utcnow()
    start = now - timedelta(days = days)

    rows = (
        db.query(
            func.date(Ticket.created_at).label("day"),
            Ticket.department,
            func.count(Ticket.id)
        )
        .filter(Ticket.created_at >= start)
        .group_by("day", Ticket.department)
        .order_by("day")
        .all()
    )

    return {
        "timeline": [
            {"date": row[0].isoformat(), "department": row[1], "count": row[2]}
            for row in rows
        ]
    }

@router.get("/trends/new-labels")
def new_labels(db: Session = Depends(get_db)):
    """
    Detect newly emerging or rapidly growing labels. 
    """
    now = datetime.utcnow()
    this_start = now - timedelta(days=7)
    last_start = now - timedelta(days=14)
    last_end = now - timedelta(days=7)

    this_week = (
        db.query(Ticket.label, func.count(Ticket.id))
        .filter(Ticket.created_at >= this_start)
        .group_by(Ticket.label)
        .all()
    )
    last_week = (
        db.query(Ticket.label, func.count(Ticket.id))
        .filter(Ticket.created_at >= last_start, Ticket.created_at < last_end)
        .group_by(Ticket.label)
        .all()
    )

    this_dict = {row[0]: row[1] for row in this_week}
    last_dict = {row[0]: row[1] for row in last_week}

    new_or_surging = []
    for label, this_count in this_dict.items():
        last_count = last_dict.get(label, 0)
        if last_count == 0 and this_count > 0:
            new_or_surging.append({"label": label, "this_week": this_count, "status": "new"})
        elif last_count > 0 and this_count >= last_count * 3:   # >200% increase
            new_or_surging.append({"label": label, "this_week": this_count, "last_week": last_count, "status": "surging"})

    return {"labels": new_or_surging}