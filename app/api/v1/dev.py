from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Optional
import numpy as np
import uuid
from app.services.ml_service_dependency import get_ml_service
from app.services.ml_services import MLService
from app.pipeline.gen_embeddings import encode_single

import textwrap, os
from pathlib import Path
from pyvis.network import Network



STATIC_DIR = Path(__file__).resolve().parents[3] / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)   

router = APIRouter(prefix = "/dev", tags = ["dev"])

class ProbeRequest(BaseModel):
    text: str

class ThresholdSweepRequest(BaseModel):
    text: str

class BatchRequest(BaseModel):
    texts: List[str]


@router.post("/probe")
def probe_embedding(req: ProbeRequest, ml: MLService = Depends(get_ml_service)):
    emb = encode_single(req.text, ml.embedder).astype(np.float32)
    result = ml.qdrant.client.query_points(
        collection_name=ml.qdrant.medoid_collection,
        query=emb[0].tolist(),
        limit=10,
        with_payload=True
    )
    points = result.points if hasattr(result, 'points') else result

    matches = []
    for hit in points:
        matches.append({
            "meta_cluster_id": hit.payload["meta_cluster_id"],
            "meta_label": hit.payload["meta_label"],
            "department": hit.payload["department"],
            "similarity": round(hit.score, 4),
        })
    return {"query": req.text, "matches": matches}

@router.post("/threshold-sweep")
def threshold_sweep(req: ThresholdSweepRequest, ml: MLService = Depends(get_ml_service)):
    thresholds = [round(x * 0.05, 2) for x in range(6, 19)]  
    medoid_best = None          
    llm_best = None            
    transition_threshold = None

    for thresh in thresholds:
        res = ml.classify(
            description=req.text,
            sim_threshold=thresh,
            generate_solution=False,
            store=False
        )
        if res["source"] == "medoid":
            if medoid_best is None or res["confidence"] > medoid_best["confidence"]:
                medoid_best = {
                    "threshold": thresh,
                    "label": res["label"],
                    "department": res["department"],
                    "confidence": res["confidence"],
                    "source": res["source"]
                }
        else:  
            if llm_best is None:
                llm_best = {
                    "threshold": thresh,
                    "label": res["label"],
                    "department": res["department"],
                    "confidence": res["confidence"],
                    "source": res["source"]
                }
                transition_threshold = thresh   

    return {
        "query": req.text,
        "medoid": medoid_best,
        "llm_fallback": llm_best,
        "transition_threshold": transition_threshold
    }


@router.get("/medoids")
def list_medoids(ml: MLService = Depends(get_ml_service)):
    points, _ = ml.qdrant.client.scroll(
        collection_name = ml.qdrant.medoid_collection,
        limit = 100,
        with_payload = True,
        with_vectors = False
    )
    medoids = []
    for pt in points:
        medoids.append({
            "id": pt.id,
            "meta_cluster_id": pt.payload["meta_cluster_id"],
            "meta_label": pt.payload["meta_label"],
            "department": pt.payload["department"],
            "ticket_count": pt.payload.get("ticket_count", 0),
        })
    
    return {"medoids": sorted(medoids, key = lambda x: x["id"])}

@router.post("/batch")
def batch_test(req: BatchRequest, ml: MLService = Depends(get_ml_service)):
    results = []
    for text in req.texts:
        if not text.strip():
            continue
        res = ml.classify(
            description=text,
            sim_threshold=0.60,   
            generate_solution=False,
            store=False
        )
        results.append({
            "text": text,
            "label": res["label"],
            "department": res["department"],
            "priority": res["priority"],
            "confidence": res["confidence"],
            "source": res["source"],
        })
    return {"results": results}

@router.post("/probe-tickets-graph")
def probe_tickets_graph(req: ProbeRequest, request: Request, ml: MLService = Depends(get_ml_service)):
    emb = encode_single(req.text, ml.embedder).astype(np.float32)

    result = ml.qdrant.client.query_points(
        collection_name=ml.qdrant.incoming_collection,
        query=emb[0].tolist(),
        limit=10,
        with_payload=True,
    )
    points = result.points if hasattr(result, 'points') else result

    net = Network(height="500px", width="100%", bgcolor="#111114", font_color="#e8e8f0")
    net.force_atlas_2based()

    query_label = textwrap.shorten(req.text, width=50, placeholder="…")
    net.add_node(0, label=query_label, title=req.text, color="#f5a623", size=25, shape="dot")

    for i, hit in enumerate(points, start=1):
        desc = hit.payload.get("description", "")[:100]
        label = f"{i}. {textwrap.shorten(desc, width=60, placeholder='…')}"
        sim = round(hit.score, 3)
        net.add_node(i, label=label, title=f"Similarity: {sim}\n{desc}", color="#60a5fa", size=15)
        net.add_edge(0, i, value=sim, title=str(sim))

    unique_name = f"network_{uuid.uuid4().hex[:8]}.html"
    filepath = str(STATIC_DIR / unique_name)
    net.save_graph(filepath)

    base_url = str(request.base_url).rstrip("/")
    return {"url": f"{base_url}/static/{unique_name}"}