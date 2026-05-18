import json, joblib, numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

# ---------- Your cloud credentials ----------
QDRANT_URL= "https://3f2dcb7f-81bb-4b32-b73a-f4404346637f.eu-central-1-0.aws.cloud.qdrant.io"
QDRANT_API_KEY= "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6YTVlZDMzMjMtYjQ2MS00OTJmLTgwMGItZjI1ZWE1MTBhOTM1In0.8Jq7rTTLOue-KhTvFeXdSr_DFJlHf2svF_IzIEXsUGU"

# ---------- Load assets ----------
medoid_vectors = joblib.load("app/ml/artifacts/medoid_vectors.pkl")
medoid_ids     = joblib.load("app/ml/artifacts/medoid_ids.pkl")

# Load the maps (both have string keys from JSON)
with open("app/ml/artifacts/meta_label_map.json") as f:
    meta_label_map_raw = json.load(f)
with open("app/ml/artifacts/cluster_to_department.json") as f:
    dept_map_raw = json.load(f)

# Helper: get label from ID (handles both int and str)
def get_label(mid):
    return meta_label_map_raw.get(str(mid), meta_label_map_raw.get(int(mid), "Unknown"))

def get_department(mid):
    return dept_map_raw.get(str(mid), dept_map_raw.get(int(mid), "Uncategorised"))

# ---------- Connect to Qdrant Cloud ----------
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# ---------- Recreate medoid collection ----------
client.recreate_collection(
    collection_name="ticket_medoids",
    vectors_config=qmodels.VectorParams(
        size=1024,
        distance=qmodels.Distance.COSINE
    )
)

# ---------- Build points with correct labels ----------
points = []
for i, meta_id in enumerate(medoid_ids):
    points.append(
        qmodels.PointStruct(
            id=i,
            vector=medoid_vectors[i].tolist(),
            payload={
                "meta_cluster_id": int(meta_id),
                "meta_label": get_label(meta_id),
                "department": get_department(meta_id),
                "type": "medoid",
                "ticket_count": 0  
            }
        )
    )

client.upsert(collection_name="ticket_medoids", points=points)
print(f"✓ Re‑uploaded {len(points)} medoids with correct labels")