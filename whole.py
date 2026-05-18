import re
import numpy as np
import pandas as pd
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_distances, cosine_similarity
import hdbscan
import cuml
import joblib
TOOL_REPLACEMENTS = {
    r'\b(kafka|rabbitmq|nats|pulsar|sqs|sns|activemq|zeromq)\b': 'msg_queue',
    r'\b(postgres|postgresql|mysql|mongodb|redis|cassandra|dynamodb|elasticsearch|clickhouse|snowflake|redshift|bigquery)\b': 'database',
    r'\b(kubernetes|k8s|eks|gke|aks|nomad|ecs)\b': 'container_platform',
    r'\b(terraform|pulumi|cloudformation|ansible|helm|argocd|flux)\b': 'iac_tool',
    r'\b(jenkins|github.actions|gitlab.ci|circleci|tekton|drone)\b': 'cicd_tool',
    r'\b(aws|gcp|azure|s3|ec2|rds|gcs|blob)\b': 'cloud_provider',
    r'\b(fastapi|django|flask|spring|rails|express|nestjs|react|flutter|kotlin|rust|golang|python|java|typescript)\b': 'app_framework',
    r'\b(mlflow|kubeflow|airflow|spark|flink|tensorflow|pytorch|xgboost)\b': 'ml_tool',
    r'\b(datadog|prometheus|grafana|pagerduty|newrelic|splunk|kibana|jaeger)\b': 'observability_tool',
}
INTENT_KEYWORDS = {
    'failing', 'crashed', 'error', 'timeout', 'unreachable', 'rejected',
    'blocked', 'stuck', 'down', 'unavailable', 'corrupted', 'missing',
    'expired', 'invalid', 'denied', 'exhausted', 'leak', 'duplicate',
    'slow', 'latency', 'lag', 'spike', 'overflow', 'oom', 'killed',
    'rotate', 'reset', 'restore', 'rollback', 'restart', 'grant', 'revoke',
    'update', 'migrate', 'deploy', 'provision', 'debug', 'investigate',
    'production', 'outage', 'blocking', 'degraded', 'data.loss', 'breach',
}
def normalize_tools(text: str) -> str:
    text = text.lower()
    for pattern, replacement in TOOL_REPLACEMENTS.items():
        text = re.sub(pattern, replacement, text)
    return text
def extract_intent_text(text: str) -> str:
    """Remove version numbers, commit hashes, IPs, ports, incident/PR numbers."""
    text = re.sub(r'\bv\d+[\.\d]+\b', '', text)
    text = re.sub(r'\b[a-f0-9]{7,40}\b', '', text)
    text = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '', text)
    text = re.sub(r':\d{2,5}\b', '', text)
    text = re.sub(r'\bpr\s*#?\d+\b', '', text)
    text = re.sub(r'\binc-?\d+\b', '', text)
    return text.strip()

df = df.drop_duplicates(subset=['description'], keep='first')

print(f"Original rows: {len(df)}")
print(f"After dedup on cleaned_text: {len(df)}")
descriptions = df['description'].tolist()

# Tool abstraction + intent extraction (for vocabulary building)
processed_texts = [extract_intent_text(normalize_tools(d)) for d in descriptions]
temp_vec = TfidfVectorizer(
    stop_words='english',
    max_features=500,
    ngram_range=(1, 2),
    sublinear_tf=True
)
temp_vec.fit(processed_texts)
all_features = set(temp_vec.get_feature_names_out())
This is the whole program remember. 
And I want to make every function as a separate .py file inside pipeline directory and use all of them in ml_sevices.py
import re
import numpy as np
import pandas as pd
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_distances, cosine_similarity
import hdbscan
import cuml
import joblib
TOOL_REPLACEMENTS = {
    r'\b(kafka|rabbitmq|nats|pulsar|sqs|sns|activemq|zeromq)\b': 'msg_queue',
    r'\b(postgres|postgresql|mysql|mongodb|redis|cassandra|dynamodb|elasticsearch|clickhouse|snowflake|redshift|bigquery)\b': 'database',
    r'\b(kubernetes|k8s|eks|gke|aks|nomad|ecs)\b': 'container_platform',
    r'\b(terraform|pulumi|cloudformation|ansible|helm|argocd|flux)\b': 'iac_tool',
    r'\b(jenkins|github.actions|gitlab.ci|circleci|tekton|drone)\b': 'cicd_tool',
    r'\b(aws|gcp|azure|s3|ec2|rds|gcs|blob)\b': 'cloud_provider',
    r'\b(fastapi|django|flask|spring|rails|express|nestjs|react|flutter|kotlin|rust|golang|python|java|typescript)\b': 'app_framework',
    r'\b(mlflow|kubeflow|airflow|spark|flink|tensorflow|pytorch|xgboost)\b': 'ml_tool',
    r'\b(datadog|prometheus|grafana|pagerduty|newrelic|splunk|kibana|jaeger)\b': 'observability_tool',
}
INTENT_KEYWORDS = {
    'failing', 'crashed', 'error', 'timeout', 'unreachable', 'rejected',
    'blocked', 'stuck', 'down', 'unavailable', 'corrupted', 'missing',
    'expired', 'invalid', 'denied', 'exhausted', 'leak', 'duplicate',
    'slow', 'latency', 'lag', 'spike', 'overflow', 'oom', 'killed',
    'rotate', 'reset', 'restore', 'rollback', 'restart', 'grant', 'revoke',
    'update', 'migrate', 'deploy', 'provision', 'debug', 'investigate',
    'production', 'outage', 'blocking', 'degraded', 'data.loss', 'breach',
}
def normalize_tools(text: str) -> str:
    text = text.lower()
    for pattern, replacement in TOOL_REPLACEMENTS.items():
        text = re.sub(pattern, replacement, text)
    return text
def extract_intent_text(text: str) -> str:
    """Remove version numbers, commit hashes, IPs, ports, incident/PR numbers."""
    text = re.sub(r'\bv\d+[\.\d]+\b', '', text)
    text = re.sub(r'\b[a-f0-9]{7,40}\b', '', text)
    text = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '', text)
    text = re.sub(r':\d{2,5}\b', '', text)
    text = re.sub(r'\bpr\s*#?\d+\b', '', text)
    text = re.sub(r'\binc-?\d+\b', '', text)
    return text.strip()

df = df.drop_duplicates(subset=['description'], keep='first')

print(f"Original rows: {len(df)}")
print(f"After dedup on cleaned_text: {len(df)}")
descriptions = df['description'].tolist()

# Tool abstraction + intent extraction (for vocabulary building)
processed_texts = [extract_intent_text(normalize_tools(d)) for d in descriptions]
temp_vec = TfidfVectorizer(
    stop_words='english',
    max_features=500,
    ngram_range=(1, 2),
    sublinear_tf=True
)
temp_vec.fit(processed_texts)
all_features = set(temp_vec.get_feature_names_out())
tool_tokens = set(TOOL_REPLACEMENTS.values())
noise_words = {'pr', 'inc', 'v1', 'v2', 'v3', 'v4', 'v5', 'v6', 'v7', 'v8', 'v9', 'v10',
               'v11', 'v12', 'v13', 'v14', 'v15', 'v16', 'v17', 'v18', 'v19', 'v20',
               'commit', 'hash', 'ip', 'port', 'pr_number', 'inc_number'}
final_vocab = sorted(all_features - tool_tokens - noise_words)
print(f"Final vocabulary size: {len(final_vocab)}")
intent_vectorizer = TfidfVectorizer(
    vocabulary=final_vocab,
    sublinear_tf=True,
    norm='l2'
)
intent_tfidf = intent_vectorizer.fit_transform(processed_texts)
INTENT_PREFIX = (
    "Represent the core problem type and required action of this support ticket, "
    "ignoring specific tool names: "
)
from sentence_transformers import SentenceTransformer
import torch
model_name = "BAAI/bge-m3"
emb_raw = embedder.encode(descriptions, batch_size=64, normalize_embeddings=True)

emb_intent = embedder.encode(
    [INTENT_PREFIX + d for d in descriptions],
    batch_size=64,
    normalize_embeddings=True
)
This is the whole program remember. 
And I want to make every function as a separate .py file inside pipeline directory and use all of them in ml_sevices.py
import re
import numpy as np
import pandas as pd
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_distances, cosine_similarity
import hdbscan
import cuml
import joblib
TOOL_REPLACEMENTS = {
    r'\b(kafka|rabbitmq|nats|pulsar|sqs|sns|activemq|zeromq)\b': 'msg_queue',
    r'\b(postgres|postgresql|mysql|mongodb|redis|cassandra|dynamodb|elasticsearch|clickhouse|snowflake|redshift|bigquery)\b': 'database',
    r'\b(kubernetes|k8s|eks|gke|aks|nomad|ecs)\b': 'container_platform',
    r'\b(terraform|pulumi|cloudformation|ansible|helm|argocd|flux)\b': 'iac_tool',
    r'\b(jenkins|github.actions|gitlab.ci|circleci|tekton|drone)\b': 'cicd_tool',
    r'\b(aws|gcp|azure|s3|ec2|rds|gcs|blob)\b': 'cloud_provider',
    r'\b(fastapi|django|flask|spring|rails|express|nestjs|react|flutter|kotlin|rust|golang|python|java|typescript)\b': 'app_framework',
    r'\b(mlflow|kubeflow|airflow|spark|flink|tensorflow|pytorch|xgboost)\b': 'ml_tool',
    r'\b(datadog|prometheus|grafana|pagerduty|newrelic|splunk|kibana|jaeger)\b': 'observability_tool',
}
INTENT_KEYWORDS = {
    'failing', 'crashed', 'error', 'timeout', 'unreachable', 'rejected',
    'blocked', 'stuck', 'down', 'unavailable', 'corrupted', 'missing',
    'expired', 'invalid', 'denied', 'exhausted', 'leak', 'duplicate',
    'slow', 'latency', 'lag', 'spike', 'overflow', 'oom', 'killed',
    'rotate', 'reset', 'restore', 'rollback', 'restart', 'grant', 'revoke',
    'update', 'migrate', 'deploy', 'provision', 'debug', 'investigate',
    'production', 'outage', 'blocking', 'degraded', 'data.loss', 'breach',
}
def normalize_tools(text: str) -> str:
    text = text.lower()
    for pattern, replacement in TOOL_REPLACEMENTS.items():
        text = re.sub(pattern, replacement, text)
    return text
def extract_intent_text(text: str) -> str:
    """Remove version numbers, commit hashes, IPs, ports, incident/PR numbers."""
    text = re.sub(r'\bv\d+[\.\d]+\b', '', text)
    text = re.sub(r'\b[a-f0-9]{7,40}\b', '', text)
    text = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '', text)
    text = re.sub(r':\d{2,5}\b', '', text)
    text = re.sub(r'\bpr\s*#?\d+\b', '', text)
    text = re.sub(r'\binc-?\d+\b', '', text)
    return text.strip()

df = df.drop_duplicates(subset=['description'], keep='first')

print(f"Original rows: {len(df)}")
print(f"After dedup on cleaned_text: {len(df)}")
descriptions = df['description'].tolist()

# Tool abstraction + intent extraction (for vocabulary building)
processed_texts = [extract_intent_text(normalize_tools(d)) for d in descriptions]
temp_vec = TfidfVectorizer(
    stop_words='english',
    max_features=500,
    ngram_range=(1, 2),
    sublinear_tf=True
)
temp_vec.fit(processed_texts)
all_features = set(temp_vec.get_feature_names_out())
tool_tokens = set(TOOL_REPLACEMENTS.values())
noise_words = {'pr', 'inc', 'v1', 'v2', 'v3', 'v4', 'v5', 'v6', 'v7', 'v8', 'v9', 'v10',
               'v11', 'v12', 'v13', 'v14', 'v15', 'v16', 'v17', 'v18', 'v19', 'v20',
               'commit', 'hash', 'ip', 'port', 'pr_number', 'inc_number'}
final_vocab = sorted(all_features - tool_tokens - noise_words)
print(f"Final vocabulary size: {len(final_vocab)}")
intent_vectorizer = TfidfVectorizer(
    vocabulary=final_vocab,
    sublinear_tf=True,
    norm='l2'
)
intent_tfidf = intent_vectorizer.fit_transform(processed_texts)
INTENT_PREFIX = (
    "Represent the core problem type and required action of this support ticket, "
    "ignoring specific tool names: "
)
from sentence_transformers import SentenceTransformer
import torch
model_name = "BAAI/bge-m3"
emb_raw = embedder.encode(descriptions, batch_size=64, normalize_embeddings=True)

emb_intent = embedder.encode(
    [INTENT_PREFIX + d for d in descriptions],
    batch_size=64,
    normalize_embeddings=True
)
umap_tmp = cuml.UMAP(n_components=15, n_neighbors=35, min_dist=0.1,
                     metric='cosine', random_state=42)

best_validity = -1
best_ratio = 0.6
blend_ratios = [0.3, 0.4, 0.5, 0.6, 0.7]
for w in blend_ratios:
    blended = emb_raw * (1-w) + emb_intent * w
    blended /= np.linalg.norm(blended, axis=1, keepdims=True)
    hyb = np.hstack([blended * 0.75,
                     intent_tfidf.toarray() * 0.25])
    reduced_tmp = umap_tmp.fit_transform(hyb)
    clusterer_tmp = hdbscan.HDBSCAN(min_cluster_size=15, min_samples=3,
                                    metric='euclidean', cluster_selection_method='eom',
                                    cluster_selection_epsilon=0.1, gen_min_span_tree=True)
    labels_tmp = clusterer_tmp.fit_predict(reduced_tmp)
    validity = clusterer_tmp.relative_validity_
    print(f"  Ratio {w:.1f}: DBCV = {validity:.4f}")
    if validity > best_validity:
        best_validity = validity
        best_ratio = w

print(f"Best blend ratio: {best_ratio:.1f} (validity: {best_validity:.4f})")
emb_blended = emb_raw * (1-best_ratio) + emb_intent * best_ratio
emb_blended /= np.linalg.norm(emb_blended, axis=1, keepdims=True)

hybrid_emb = np.hstack([
    emb_blended * 0.75,
    intent_tfidf.toarray() * 0.25
])

hybrid_emb /= np.linalg.norm(hybrid_emb, axis=1, keepdims=True)
umap_model = cuml.UMAP(
    n_components=15,
    n_neighbors=35,  
    min_dist=0.1,        
    metric='cosine',
    random_state=42
)
reduced = umap_model.fit_transform(hybrid_emb)
reduced_np = cp.asnumpy(reduced)
clusterer = hdbscan.HDBSCAN(
    min_cluster_size=18,    
    min_samples=3,
    metric='euclidean',
    cluster_selection_method='eom',
    cluster_selection_epsilon=0.1,
    prediction_data=True
)
labels_raw = clusterer.fit_predict(reduced_np)
n_clusters = len(set(labels_raw)) - (1 if -1 in labels_raw else 0)
noise_pct = (labels_raw == -1).sum() / len(labels_raw) * 100
print(f"Raw HDBSCAN: {n_clusters} clusters, {noise_pct:.1f}% noise")
def get_medoid(embs, indices):
    """indices are global positions; returns medoid index (global)."""
    cluster_embs = embs[indices]
    dist_mat = cosine_distances(cluster_embs)
    medoid_in = np.argmin(dist_mat.mean(axis=1))
    return indices[medoid_in]
embeddings_np = emb_raw 
unique_labels = set(labels_raw) - {-1}
medoid_map = {}
for lab in unique_labels:
    idxs = np.where(labels_raw == lab)[0]
    medoid_map[lab] = embeddings_np[get_medoid(embeddings_np, idxs)] 
labels_reassigned = labels_raw.copy()
noise_indices = np.where(labels_reassigned == -1)[0]
THRESHOLD = 0.35  # cosine distance, lower = stricter

for idx in noise_indices:
    vec = embeddings_np[idx]
    best_lab, best_dist = -1, 1.0
    for lab, med in medoid_map.items():
        d = cosine_distances([vec], [med])[0,0]
        if d < best_dist:
            best_dist, best_lab = d, lab
    if best_lab != -1 and best_dist < THRESHOLD:
        labels_reassigned[idx] = best_lab

n_noise_after = (labels_reassigned == -1).sum()
print(f"After reassignment: {n_noise_after} noise points ({n_noise_after/len(labels_reassigned)*100:.1f}%)")
MIN_KEEP = 10
labels_final = labels_reassigned.copy()
unique_final = set(labels_final) - {-1}
sizes = {lab: (labels_final == lab).sum() for lab in unique_final}
for small_lab in sorted([l for l, sz in sizes.items() if sz < MIN_KEEP]):
    idx_small = np.where(labels_final == small_lab)[0]
    med_small = embeddings_np[get_medoid(embeddings_np, idx_small)]
    best_target, best_dist = -1, 1.0
    for large_lab in [l for l, sz in sizes.items() if sz >= MIN_KEEP]:
        idx_large = np.where(labels_final == large_lab)[0]
        med_large = embeddings_np[get_medoid(embeddings_np, idx_large)]
        d = cosine_distances([med_small], [med_large])[0,0]
        if d < best_dist:
            best_dist, best_target = d, large_lab
    if best_target != -1 and best_dist < 0.5:
        labels_final[labels_final == small_lab] = best_target
        print(f"  Merged tiny cluster {small_lab} ({sizes[small_lab]} tix) → {best_target}")
    else:
        labels_final[labels_final == small_lab] = -1
        print(f"  Marked tiny cluster {small_lab} ({sizes[small_lab]} tix) as noise (no close neighbour)")
unique_final = set(labels_final) - {-1}
sizes_final = {lab: (labels_final == lab).sum() for lab in unique_final}
print(f"Final clusters: {len(unique_final)}, final noise: {(labels_final == -1).sum()}")

from sklearn.metrics.pairwise import cosine_distances
from sklearn.cluster import AgglomerativeClustering
fine_labels = labels_final   
unique_fine = sorted([l for l in set(fine_labels) if l != -1])

medoid_embs = []          
medoid_labels = []        
def get_medoid(embs, indices):
    cluster_embs = embs[indices]
    dist_mat = cosine_distances(cluster_embs)
    medoid_in = np.argmin(dist_mat.mean(axis=1))
    return indices[medoid_in]
for cid in unique_fine:
    idxs = np.where(fine_labels == cid)[0]
    medoid_idx = get_medoid(embeddings_np, idxs)
    medoid_embs.append(embeddings_np[medoid_idx])
    medoid_labels.append(cid)

medoid_embs = np.array(medoid_embs)
N_META = 45

agg = AgglomerativeClustering(
    n_clusters=N_META,
    metric='cosine',
    linkage='average'
)
meta_labels = agg.fit_predict(medoid_embs)
fine_to_meta = {fine: meta for fine, meta in zip(medoid_labels, meta_labels)}

meta_final = np.full_like(fine_labels, -1, dtype=int)
for idx in range(len(fine_labels)):
    if fine_labels[idx] != -1:
        meta_final[idx] = fine_to_meta[fine_labels[idx]]
for meta_id in sorted(set(meta_final) - {-1}):
    idxs = np.where(meta_final == meta_id)[0]
    if len(idxs) < 5:
        continue
    medoid_idx = get_medoid(embeddings_np, idxs)
    medoid_vec = embeddings_np[medoid_idx].reshape(1, -1)
    cluster_embs = embeddings_np[idxs]
    dists = cosine_distances(cluster_embs, medoid_vec).ravel()
    sorted_order = np.argsort(dists)
    top_k = min(10, len(idxs))
    top_indices = idxs[sorted_order[:top_k]]

    print(f"\n{'='*60}")
    print(f"Meta‑Cluster {meta_id} – {len(idxs)} tickets")
    print(f"{'='*60}")
    for rank, idx in enumerate(top_indices, 1):
        preview = descriptions[idx].replace('\n', ' ').strip()[:200]
        print(f" {rank:2d}. {preview}")
valid_meta = [m for m in set(meta_final) if m != -1]

medoid_vectors = []
medoid_ids = []

for meta_id in sorted(valid_meta):
    idxs = np.where(meta_final == meta_id)[0]
    medoid_idx = get_medoid(embeddings_np, idxs)  
    medoid_vectors.append(embeddings_np[medoid_idx])
    medoid_ids.append(meta_id)
medoid_vectors = np.array(medoid_vectors)
medoid_vectors = medoid_vectors   
medoid_ids = medoid_ids           
meta_label_map = meta_label_map      
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
from sklearn.metrics import classification_report
|mask = df['priority'].notna()
X = embeddings_np[mask]        
y = df.loc[mask, 'priority'].values
le = LabelEncoder()
y_enc = le.fit_transform(y)
X_train, X_test, y_train, y_test = train_test_split(
    X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
)
model = XGBClassifier(
    n_estimators=200,
    learning_rate=0.1,
    max_depth=6,
    random_state=42,
    eval_metric='mlogloss'
)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred, target_names=le.classes_))
import re

URGENCY_PATTERNS = {
    'production_down':    r'\b(production|prod)\b.{0,30}\b(down|outage|failing|crashed)\b',
    'data_loss':          r'\b(data.loss|corruption|duplicate.charge|double.charge)\b',
    'revenue_impact':     r'\b(revenue|customer.facing|blocking.all|cannot.trade|cannot.pay)\b',
    'security_critical':  r'\b(breach|exploit|injection|exposure|compromised)\b',
    'rollback_needed':    r'\b(roll.?back|revert|immediate)\b',
    'local_only':         r'\b(local|localhost|my.laptop|my.machine|dev.env)\b',
    'cosmetic':           r'\b(typo|tooltip|dark.mode|font|icon|label)\b',
    'access_request':     r'\b(need.access|request.access|read.only|temporary.access)\b',
    'how_to':             r'\b(how.do.i|how.can.i|is.there.a.way|can.we.add)\b',
    'quota_request':      r'\b(quota|limit.increase|more.resources)\b',
}
def extract_urgency_features(description: str) -> np.ndarray:
    text = description.lower()
    features = []
    for pattern in URGENCY_PATTERNS.values():
        features.append(1.0 if re.search(pattern, text) else 0.0)
    features.append(len(description) / 1000.0)             
    features.append(1.0 if 'error' in text else 0.0)
    features.append(1.0 if 'exception' in text else 0.0)
    features.append(text.count('%') / 10.0)                 
    return np.array(features, dtype=np.float32)

urgency_features = np.array([
    extract_urgency_features(d) for d in descriptions
])
print(f"Urgency feature shape: {urgency_features.shape}")

X_combined = np.hstack([embeddings_np, urgency_features])
mask = df['priority'].notna()
X = X_combined[mask]
y = df.loc[mask, 'priority'].values
le = LabelEncoder()
y_enc = le.fit_transform(y)
X_train, X_test, y_train, y_test = train_test_split(
    X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
)
from collections import Counter
class_counts = Counter(y_train)
total = sum(class_counts.values())
scale_pos_weight = {
    cls: total / (len(class_counts) * count)
    for cls, count in class_counts.items()
}
sample_weights = np.array([scale_pos_weight[y] for y in y_train])
model = XGBClassifier(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=5,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    eval_metric='mlogloss'
)
model.fit(
    X_train, y_train,
    sample_weight=sample_weights,
    eval_set=[(X_test, y_test)],
    verbose=False
)
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred, target_names=le.classes_))
def llm_generate_solution(description: str, label: str, priority: str,
                          similar_tickets: list) -> str:
    """Generate a solution for a classified ticket (medoid path)."""
    context = "\n".join([
        f"- [{t['similarity']:.2f}] {t['description']}"
        for t in similar_tickets[:3]
    ])
    prompt = f"""You are a senior IT operations expert. A support ticket has been classified as follows:

TICKET: {description}
CATEGORY: {label}
PRIORITY: {priority}

Most similar past tickets:
{context}

Write a clear, step‑by‑step resolution plan (under 150 words). Return ONLY a JSON object with the key "solution". /no_think"""
    try:
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=LLM_MODEL,
            temperature=0.2,
            max_tokens=400,
        )
        raw = response.choices[0].message.content
        json_str = extract_json(raw) 
        result = json.loads(json_str)
        return result.get("solution") or "A solution could not be generated."
    except Exception:
        return "Solution generation temporarily unavailable."
def extract_json(text: str) -> str:
    """
    Extract a JSON object from raw LLM output that may contain markdown fences,
    thinking blocks, or trailing text.
    """
    # Remove thinking blocks if present
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    # Try to find a JSON object
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        return m.group(0)
    return text.strip()
def llm_fallback_free(description: str, max_retries: int = 2) -> dict:
    prompt = f"""You are an expert IT support triage assistant. For the ticket below, provide a short, descriptive category label (e.g., "Office Wi‑Fi Connectivity Issue", "Database Credential Expiry", "Build Memory Exhaustion") and a step‑by‑step solution (under 150 words).

Return ONLY a valid JSON object. Do NOT include any markdown fences, explanations, or extra text. The JSON must have exactly two keys:
- "label": your short category label
- "solution": your step‑by‑step solution

Ticket: {description} /no_think"""

    for attempt in range(max_retries):
        try:
            response = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=LLM_MODEL,
                temperature=0.1,
                max_tokens=500,
            )
            raw = response.choices[0].message.content
            json_str = extract_json(raw)                     # <-- robust extraction
            result = json.loads(json_str)
            label = result.get("label", "").strip()
            solution = result.get("solution") or "A solution could not be generated."
            if label:
                return {"label": label, "solution": solution}
        except Exception:
            if attempt == max_retries - 1:
                return {"label": "Uncategorised / Rare Issues",
                        "solution": "Unable to generate solution – please check the ticket manually."}
    return {"label": "Uncategorised / Rare Issues",
            "solution": "Unable to generate solution – please check the ticket manually."}
def classify_ticket_medoid_llm(
    description: str,
    sim_threshold: float = 0.60,
    llm_solution: bool = True,
    llm_fallback: bool = True
) -> dict:
    raw_emb = embedder.encode([description], normalize_embeddings=True).astype('float32')
    urg_feat = extract_urgency_features(description).reshape(1, -1)
    combined_emb = np.hstack([raw_emb, urg_feat])

    priority = le.inverse_transform(model.predict(combined_emb))[0]

    # 2. Medoid search (label only)
    sims = cosine_similarity(raw_emb, medoid_vectors).flatten()
    best_idx = np.argmax(sims)
    best_sim = sims[best_idx]

    label = None
    department = None
    solution = None
    source = None

    if best_sim >= sim_threshold:
        meta_id = medoid_ids[best_idx]
        label = meta_label_map[meta_id]
        department = cluster_to_department.get(meta_id, "Uncategorised")
        source = "medoid"
        if llm_solution:
            sims_all = cosine_similarity(raw_emb, inference_embs).flatten()
            top_k_idx = np.argsort(sims_all)[-5:][::-1]
            top_k_sims = sims_all[top_k_idx]
            similar_ctx = [{
                'similarity': round(float(top_k_sims[i]), 4),
                'description': inference_descs[idx][:250]
            } for i, idx in enumerate(top_k_idx)]
            solution = llm_generate_solution(description, label, priority, similar_ctx)
    else:
        if llm_fallback:
            try:
                llm_res = llm_fallback_free(description)   # no label map – free form
                label = llm_res["label"]
                solution = llm_res["solution"]
                department = "Uncategorised"
                source = "llm_fallback"
            except Exception:
                label = "Uncategorised / Rare Issues"
                department = "Uncategorised"
                solution = "LLM fallback error."
                source = "error"
        else:
            label = "Uncategorised / Rare Issues"
            department = "Uncategorised"
            solution = "No fallback configured."
            source = "none"

    if label is None or label == "":
        label = "Uncategorised / Rare Issues"
    if solution is None or solution == "":
        solution = "No solution available."
    if department is None:
        department = "Uncategorised"

    sims_all = cosine_similarity(raw_emb, inference_embs).flatten()
    top_k_idx = np.argsort(sims_all)[-5:][::-1]
    top_k_sims = sims_all[top_k_idx]
    similar = [{
        'similarity': round(float(top_k_sims[i]), 4),
        'description': inference_descs[idx][:250]
    } for i, idx in enumerate(top_k_idx)]

    return {
        "label": label,
        "department": department,
        "confidence": round(best_sim, 4),
        "priority": priority,
        "source": source,
        "solution": solution,
        "similar_tickets": similar
    }