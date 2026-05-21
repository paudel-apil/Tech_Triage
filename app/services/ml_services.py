"""
Main machine learning orchestration service. 

This module acts as a central AI application coordinator for the
Technical Support Ticket Platform.
"""

import json
import time
import numpy as np
from app.pipeline.gen_embeddings import load_embedder, encode_single
from app.pipeline.priority_classifier import PriorityClassifier
from .llm_services import LLMService
from .qdrant_services import QdrantService  


class MLService:
    """
    Central orchestration service for the AI support ticket pipeline. 
    This is a unified intelligence layer of the platform.
    """
    def __init__(self, asset_dir: str = "/app/ml/artifacts",
                 qdrant_url: str = "http://localhost:6333",
                 qdrant_api_key: str = None):
        """
        Initializes all ML Pipeline components. 
        """
        self.embedder = load_embedder()
        _ = self.embedder.encode(["warmup"], normalize_embeddings=True)

        with open(f"{asset_dir}/meta_label_map.json") as f:
            raw_meta = json.load(f)
        with open(f"{asset_dir}/cluster_to_department.json") as f:
            raw_dept = json.load(f)

        self.meta_label_map = {}
        for k, v in raw_meta.items():
            self.meta_label_map[int(k)] = v
            self.meta_label_map[str(k)] = v
        
        self.department_map = {}
        for k, v in raw_dept.items():
            self.department_map[int(k)] = v
            self.department_map[str(k)] = v

        self.priority_clf = PriorityClassifier(asset_dir)

        self.qdrant = QdrantService(url = qdrant_url, api_key = qdrant_api_key)

        self.llm = None             # LLM service is attached later optionally

    def set_llm(self, llm_service: LLMService) -> None:
        """
        Attach an LLM service for solution generation and fallback.
        """
        self.llm = llm_service

    def classify(self, description: str, sim_threshold: float = 0.60,
                 generate_solution: bool = False, store: bool = True) -> dict:
        """
        Classify a ticket. If store = true, persist in incoming collection.

        Run the complete AI classification pipeline for a support ticket. 
        """
        raw_emb = encode_single(description, self.embedder)

        priority = self.priority_clf.predict(description, raw_emb)

        medoid_result = self.qdrant.classify_by_medoid(raw_emb, sim_threshold)

        label = medoid_result["label"]
        department = medoid_result["department"]
        confidence = medoid_result["confidence"]
        source = medoid_result["source"]
        meta_id = medoid_result["meta_cluster_id"]

        if department.lower() == "uncategorized":
            department = "Uncategorised"

        similar = self.qdrant.search_similar(raw_emb, limit=5)

        solution = None
        if source in ("no_medoid_match", "low_confidence") and self.llm:
            try:
                llm_res = self.llm.fallback_free(description)
                label = llm_res["label"]
                department = "Uncategorised"
                solution = llm_res["solution"]
                source = "llm_fallback"
            except Exception:
                source = "error"
        elif generate_solution and self.llm:
            try:
                solution = self.llm.generate_solution(
                    description, label, priority, similar
                )
            except Exception:
                solution = None

        point_id = None
        created_at = None

        return {
            "id": point_id,
            "description": description,
            "created_at": created_at,
            "label": label,
            "department": department,
            "confidence": confidence,
            "priority": priority,
            "source": source,
            "solution": solution,
            "similar_tickets": similar
        }
    
    def list_incoming_tickets(self, limit: int = 20, offset: int = 0) -> tuple:
        """
        Return (ticket_list, ticket_count) from the incoming collection.
        """
        points, total = self.qdrant.scroll_incoming(limit = limit, offset = offset)
        tickets = []
        for point in points:
            payload = point.payload or {}
            tickets.append({
                "id": point.id,
                "description": payload.get("description", ""),
                "created_at": payload.get("classified_at", ""),
                "label": payload.get("assigned_label", ""),
                "department": payload.get("department", ""),
                "priority": payload.get("priority", ""),
                "confidence": payload.get("confidence", 0.0),
                "source": payload.get("source", ""),
                "solution": None,
                "similar_tickets": []
            })
        return tickets, total
    
    def search_incoming(self, query: str, limit: int = 10) -> list:
        """
        Embed the query and search the incoming collection.
        """
        emb = encode_single(query, self.embedder)
        return self.qdrant.search_similar(emb, limit = limit)

    def similar_to_ticket(self, ticket_id: int, limit: int = 5) -> list:
        """
        Retrieve the stored embedding for ticket_id, then search similar.
        """
        point = self.qdrant.retrieve_point(ticket_id)
        if not point or not point.vector:
            raise ValueError("Ticket not found or has no vector")
        emb = np.array(point.vector).reshape(1, -1).astype(np.float32)
        return self.qdrant.search_similar(emb, limit = limit)