"""
Priority classification utilities for support ticket triaging.

This module is responsible for extracting urgency-related features from ticket text,
combining semantic embeddings with handcrafted signals and predicting ticket priority
levels using a trained ML Model.
"""

import re
import numpy as np
import joblib

URGENCY_PATTERNS = {
    'production_down':   r'\b(production|prod)\b.{0,30}\b(down|outage|failing|crashed)\b',
    'data_loss':         r'\b(data.loss|corruption|duplicate.charge|double.charge)\b',
    'revenue_impact':    r'\b(revenue|customer.facing|blocking.all|cannot.trade|cannot.pay)\b',
    'security_critical': r'\b(breach|exploit|injection|exposure|compromised)\b',
    'rollback_needed':   r'\b(roll.?back|revert|immediate)\b',
    'local_only':        r'\b(local|localhost|my.laptop|my.machine|dev.env)\b',
    'cosmetic':          r'\b(typo|tooltip|dark.mode|font|icon|label)\b',
    'access_request':    r'\b(need.access|request.access|read.only|temporary.access)\b',
    'how_to':            r'\b(how.do.i|how.can.i|is.there.a.way|can.we.add)\b',
    'quota_request':     r'\b(quota|limit.increase|more.resources)\b',
}

def extract_urgency_features(description: str) -> np.ndarray:
    """
    Extract handcrafted urgency-related numerical features from ticket text.
    Returns np.ndarray Numerical feature vector representing urgency signals
    """
    text = description.lower()
    features = []
    for pattern in URGENCY_PATTERNS.values():
        features.append(1.0 if re.search(pattern, text) else 0.0)
    
    features.append(len(description) / 1000.0)
    features.append(1.0 if 'error' in text else 0.0)
    features.append(1.0 if 'exception' in text else 0.0)
    features.append(text.count('%') / 10.0)
    return np.array(features, dtype = np.float32)

class PriorityClassifier:
    """
    Machine learning wrapper for support ticket priority prediction.
    This classifier combines semantic embeddings with handcrafted urgency features.
    """
    def __init__(self, asset_dir: str = '/app/ml/artifacts'):
        self.model = joblib.load(f"{asset_dir}/priority_xgb_model.pkl")
        self.le = joblib.load(f"{asset_dir}/priority_label_encoder.pkl")

    def predict(self, description: str, raw_embeddings: np.ndarray) -> str:
        urg_feat = extract_urgency_features(description).reshape(1, -1)
        combined = np.hstack([raw_embeddings, urg_feat])
        pred_enc = self.model.predict(combined)[0]
        return self.le.inverse_transform([pred_enc])[0]
    