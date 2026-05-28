import time
import numpy as np
from typing import Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

class QdrantService:
    """
    Handles Qdrant collections for medoid classification and incoming ticket storage.
    """
    def __init__(self, url: str, api_key: str):
        self.client = QdrantClient(url = url, api_key = api_key)
        self.medoid_collection = "ticket_medoids"
        self.incoming_collection = "incoming_tickets"
        self._counter = int(time.time())

    def setup_medoids(self, medoid_vectors: np.ndarray, medoid_ids: list,
                      meta_label_map: dict, cluster_to_department: dict,
                      meta_final: np.ndarray) -> None:
        """
        Create/recreate the medoid collection and upload medoid vectors.
        """
        self.client.recreate_collection(
            collection_name = self.medoid_collection,
            vectors_config = qmodels.VectorParams(
                size = medoid_vectors.shape[1],
                distance = qmodels.Distance.COSINE
            )
        )

        points = []
        for i, meta_id in enumerate(medoid_ids):
            points.append(
                qmodels.PointStruct(
                    id = i,
                    vector = medoid_vectors[i].tolist(),
                    payload = {
                        "meta_cluster_id": int(meta_id),
                        "meta_label": meta_label_map.get(meta_id, "Unknown"),
                        "department": cluster_to_department.get(meta_id, "Uncategorized"),
                        "type": "medoid",
                        "ticket_count": int((meta_final == meta_id).sum())
                    }
                )
            )
        self.client.upsert(collection_name = self.medoid_collection, points = points)

    def setup_incoming(self) -> None:
        """
        Create/recreate the incoming tickets collection (empty).
        """
        self.client.recreate_collection(
            collection_name = self.incoming_collection,
            vectors_config = qmodels.VectorParams(
                size = 1024,
                distance = qmodels.Distance.COSINE
            )
        )

    def classify_by_medoid(self, embedding: np.ndarray,
                           sim_threshold: float = 0.60) -> dict:
        """
        Search the medoid collection and return the best match.
        """
        result = self.client.query_points(
            collection_name = self.medoid_collection,
            query = embedding[0].tolist(),
            limit = 1,
            with_payload = True
        )
        points = result.points if hasattr(result, 'points') else result

        if not points:
            return {
                "label": "Uncategorized / Rare Issues",
                "department": "Uncategorized",
                "meta_cluster_id": -1,
                "confidence": 0.0,
                "source": "no_medoids_match"
            }

        best = points[0]
        score = best.score

        if score >= sim_threshold:
            return {
                "label": best.payload["meta_label"],
                "department": best.payload["department"],
                "meta_cluster_id": best.payload["meta_cluster_id"],
                "confidence": round(score, 4),
                "source": "medoid"
            }
        else:
            return {
                "label": "Uncategorized / Rare Issues",
                "department": "Uncategorized",
                "meta_cluster_id": -1,
                "confidence": round(score, 4),
                "source": "low_confidence"
            }
        
    def search_similar(self, embedding: np.ndarray,
                       limit: int = 5) -> list[dict]:
        """
        Search the incoming collection for similar tickets.
        """ 
        result = self.client.query_points(
            collection_name = self.incoming_collection,
            query = embedding[0].tolist(),
            limit = limit,
            with_payload = True
        )

        points = result.points if hasattr(result, 'points') else result

        return [{
            "id": hit.id,
            "similarity": round(hit.score, 4),
            "description": hit.payload.get("description", "")[:250],
            "label": hit.payload.get("assigned_label", ""),
            "department": hit.payload.get("department", ""),
            "priority": hit.payload.get("priority", ""),
            "source": hit.payload.get("source", ""),
            "confidence": hit.payload.get("confidence", ""),
            "classified_at": hit.payload.get("classified_at", ""),
        }for hit in points]
    
    def store_incoming(self, embedding: np.ndarray, description: str,
                       label: str, department: str, priority: str,
                       source: str, confidence: float,
                       meta_cluster_id: int) -> None:
        """Store a newly classified ticket in the incoming collection."""
        point_id = self._counter
        self._counter += 1

        self.client.upsert(
            collection_name=self.incoming_collection,
            points=[
                qmodels.PointStruct(
                    id=point_id,
                    vector=embedding[0].tolist(),
                    payload={
                        "description": description,
                        "assigned_label": label,
                        "department": department,
                        "priority": priority,
                        "source": source,
                        "confidence": confidence,
                        "meta_cluster_id": meta_cluster_id,
                        "classified_at": time.strftime(
                            "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
                        )
                    }
                )
            ]
        )
        return point_id
    
    def scroll_incoming(self, limit: int, offset: int) -> tuple:
        """
        Scroll through incoming collection, return (points, total).
        """
        count = self.client.count(collection_name = self.incoming_collection).count
        if offset >= count:
            return [], count
        results = self.client.scroll(
            collection_name = self.incoming_collection,
            limit = limit,
            offset = offset,
            with_payload = True,
            with_vectors = False,
        )
        return results[0], count
    
    def retrieve_point(self, point_id: int) -> Optional[dict]:
        """
        Retrieve a single point by ID.
        """
        results = self.client.retrieve(
            collection_name=self.incoming_collection,
            ids=[point_id],
            with_vectors=True,
            with_payload=True
        )
        return results[0] if results else None
    
    def get_stats(self) -> dict:
        """
        Return basic stats about the incoming collection.
        """
        count = self.client.count(collection_name = self.incoming_collection).count
        medoid_count = self.client.count(collection_name = self.medoid_collection).count
        return {
            "medoids": medoid_count,
            "total_classified": count
        }

    