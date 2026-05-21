"""
Embedding utilities for generating semantic vector representations
from support ticket descriptions.
"""

import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = 'BAAI/bge-m3'
INTENT_PREFIX = (
    "Represent the core problem type and required action of this support ticket, "
    "ignoring specific tool names: "
)

def load_embedder(model_name: str = MODEL_NAME, device: str = 'cpu'):
    return SentenceTransformer(model_name, device = device)

def encode_single(description: str, embedder: SentenceTransformer) -> np.ndarray:
    """
    Encode a single description -> (1, 1024) float32.
    """
    emb = embedder.encode([description], normalize_embeddings = True)
    return emb.astype(np.float32)
