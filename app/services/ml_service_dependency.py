"""
Dependency injection and singleton initialization for ML services. 

This module provides a centralized way to initialize and access the
application's AI/ML pipeline services. 
"""

from app.services.ml_services import MLService
from app.services.llm_services import LLMService
from app.core.config import settings

_ml_service_instance = None

def get_ml_service() -> MLService:
    """
    Return the shared ML service instance.
    """
    global _ml_service_instance
    if _ml_service_instance is None:
        _ml_service_instance = MLService(
            asset_dir = "./app/ml/artifacts",
            qdrant_url = settings.QDRANT_URL,
            qdrant_api_key = settings.QDRANT_API_KEY
        )
        llm = LLMService(api_key = settings.GROQ_API_KEY)
        _ml_service_instance.set_llm(llm)

    return _ml_service_instance