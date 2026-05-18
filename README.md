# TicketIQ

**ML-powered IT support ticket triage.** TicketIQ automatically classifies incoming support tickets into 45 curated intent categories, predicts priority, routes to the right department, and generates actionable resolution plans — all in under two seconds.

Built with BGE-M3 embeddings, HDBSCAN clustering, XGBoost, Qdrant, Groq (Qwen3-32B), FastAPI, and a Reflex frontend.

---

## Live Demo

| | Link |
|---|---|
| **Backend API** | [huggingface.co/spaces/paudelapil/Tech_Triage](https://huggingface.co/spaces/paudelapil/Tech_Triage) |
| **API Docs** (Swagger) | [paudelapil-tech-triage.hf.space/docs](https://paudelapil-tech-triage.hf.space/docs) |
| **Frontend UI** | [paudelapil/Tech_Triage_Frontend](https://huggingface.co/spaces/paudelapil/Tech_Triage_Frontend) |

---

## How It Works

Every ticket submitted goes through a five-step pipeline:

```
Ticket text
    │
    ├─ 1. BGE-M3 (1024-d embedding)
    │
    ├─ 2. XGBoost priority classifier
    │       └─ raw embedding + 14 urgency features → low / medium / high
    │
    ├─ 3. Qdrant medoid search (60 pre-computed cluster centroids)
    │       ├─ similarity ≥ 0.60 → known category + LLM solution
    │       └─ similarity < 0.60 → Groq Qwen3-32B free-form label + solution
    │
    ├─ 4. Store → NeonDB (PostgreSQL) + Qdrant incoming_tickets collection
    │
    └─ 5. Return → label, department, priority, confidence, solution, similar tickets
```

The 45 intent categories were built by clustering ~7,500 synthetic fintech IT tickets using a hybrid embedding (BGE-M3 + intent-prefixed BGE-M3 blended at 0.6/0.4 + TF-IDF intent vocabulary), then merging 110 HDBSCAN micro-clusters into 45 meta-clusters via agglomerative clustering. Examples:

- *Stream Processing Checkpoint & State Recovery Failures*
- *OAuth Token Expiry & Automated Secret Refresh Failures*
- *Cache Memory Pressure & Aggressive Eviction*
- *GPU Training Resource Exhaustion – CUDA OOM & NCCL Timeouts*

---

## Tech Stack

| Layer | Technology |
|---|---|
| Embeddings | `BAAI/bge-m3` via Sentence-Transformers (1024-d) |
| Clustering | HDBSCAN + Agglomerative (110 → 45 meta-clusters) |
| Classification | Qdrant cosine similarity over 60 medoid vectors |
| Priority | XGBoost + 14 hand-crafted urgency features |
| LLM | Groq API — `qwen/qwen3-32b` |
| Vector DB | Qdrant Cloud (2 collections) |
| Database | PostgreSQL — NeonDB |
| Backend | FastAPI + SQLAlchemy + Uvicorn |
| Frontend | Reflex (Python → React) |
| Deployment | Docker on Hugging Face Spaces |

---

## Project Structure

```
ticketiq/
├── backend/
│   ├── app/
│   │   ├── main.py                      # FastAPI app, CORS, router
│   │   ├── core/config.py               # Pydantic settings
│   │   ├── db/
│   │   │   ├── models.py                # Ticket ORM model
│   │   │   └── session.py               # SQLAlchemy session / get_db
│   │   ├── api/v1/tickets.py            # REST endpoints
│   │   ├── services/
│   │   │   ├── ml_services.py           # Classification orchestrator
│   │   │   ├── qdrant_services.py       # Qdrant wrapper
│   │   │   ├── llm_services.py          # Groq client
│   │   │   └── ml_service_dependency.py # Singleton provider
│   │   ├── pipeline/
│   │   │   ├── gen_embeddings.py        # BGE-M3 encode_single()
│   │   │   ├── priority_classifier.py   # Urgency features + XGBoost
│   │   │   └── intent_classifier.py     # Training-only (TF-IDF vocab)
│   │   └── ml/artifacts/                # Serialised models & maps
│   │       ├── medoid_vectors.pkl
│   │       ├── medoid_ids.pkl
│   │       ├── meta_label_map.json
│   │       ├── cluster_to_department.json
│   │       ├── priority_xgb_model.pkl
│   │       └── priority_label_encoder.pkl
│   ├── Dockerfile
│   └── requirements.txt
│
└── frontend/
    ├── ticketiq/
    │   ├── ticketiq.py                  # App layout + sidebar
    │   ├── state.py                     # Reflex state + async HTTP calls
    │   ├── card.py                      # TicketCard component
    │   ├── submit.py                    # Submit page
    │   ├── tickets_list.py              # Tickets list page
    │   ├── search.py                    # Search page
    │   └── ui.py                        # Shared atoms (badges, bars)
    ├── assets/
    ├── rxconfig.py
    ├── Dockerfile
    └── requirements.txt
```

---

## API Reference

Base URL: `https://<backend-space>.hf.space/api/v1`

### POST `/tickets/`
Classify and store a new ticket.

**Request**
```json
{ "description": "Redis cache is evicting keys aggressively; API responses are slow." }
```

**Response**
```json
{
  "id": 42,
  "description": "Redis cache is evicting keys aggressively; API responses are slow.",
  "created_at": "2026-05-18T12:34:56Z",
  "label": "Cache Memory Pressure & Aggressive Eviction (Redis)",
  "department": "Database & Data Engineering",
  "priority": "high",
  "confidence": 0.78,
  "source": "medoid",
  "solution": "1. Connect to the Redis CLI and run INFO memory...",
  "similar_tickets": [{ "similarity": 0.91, "description": "..." }]
}
```

### GET `/tickets/`
List classified tickets with pagination.

| Param | Type | Default | Description |
|---|---|---|---|
| `limit` | int | 20 | Tickets per page (max 100) |
| `offset` | int | 0 | Pagination offset |

### POST `/tickets/search`
Semantic search across the `incoming_tickets` Qdrant collection.

```json
{ "query": "Kafka consumer lag downstream ML timeout" }
```

### GET `/tickets/{id}/similar`
Return tickets similar to a given ticket ID.

| Param | Type | Default |
|---|---|---|
| `limit` | int | 5 |

Full interactive docs at `/docs` (Swagger UI).

---

## Running Locally

### Prerequisites

- Python 3.11+
- Node.js (for Reflex)
- A [Qdrant Cloud](https://qdrant.tech) cluster
- A [Groq API key](https://console.groq.com)
- A [NeonDB](https://neon.tech) PostgreSQL database (or any Postgres)

### Backend

```bash
cd backend
pip install -r requirements.txt

# Create .env
cat > .env << 'EOF'
DATABASE_URL=postgresql://user:pass@ep-xyz.neon.tech/db?sslmode=require
QDRANT_URL=https://your-cluster.qdrant.io:6333
QDRANT_API_KEY=your-qdrant-key
GROQ_API_KEY=your-groq-key
SECRET_KEY=any-random-string
EOF

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# → http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
pip install reflex httpx

# state.py already points to localhost:8000 by default
reflex run
# → http://localhost:3000
```

---

## Deployment (Hugging Face Spaces)

Both the backend and frontend run as Docker Spaces on Hugging Face.

**Backend Space**

1. Create a new Docker Space.
2. Copy the `backend/` folder (including its `Dockerfile`) into the Space repo.
3. Add environment variables under **Settings → Repository secrets**:
   `DATABASE_URL`, `QDRANT_URL`, `QDRANT_API_KEY`, `GROQ_API_KEY`, `SECRET_KEY`
4. Push — the Space builds and starts automatically.

**Frontend Space**

1. Create another Docker Space.
2. Copy the `frontend/` folder into the Space repo.
3. Update `API_BASE` in `ticketiq/state.py`:
   ```python
   API_BASE = "https://<backend-space>.hf.space/api/v1/tickets"
   ```
4. Add the frontend Space origin to the backend's CORS `allow_origins` list.
5. Push.

---

## Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `QDRANT_URL` | Qdrant Cloud cluster endpoint |
| `QDRANT_API_KEY` | Qdrant API key |
| `GROQ_API_KEY` | Groq API key |
| `SECRET_KEY` | Arbitrary secret (FastAPI internals) |

---

## Classification Pipeline (Training)

The 45 intent categories were derived from ~7,500 synthetic fintech IT support tickets:

1. **Deduplication** — exact string dedup, then cosine-similarity dedup at ≥ 0.97 threshold.
2. **Preprocessing** — tool names replaced with generic tokens (`kafka` → `msg_queue`), noise stripped (version numbers, IPs, commit hashes).
3. **Hybrid embedding** — `0.6 × intent-prefixed BGE-M3 + 0.4 × raw BGE-M3`, concatenated with a 25% weight TF-IDF intent vocabulary matrix. Best blend ratio selected by DBCV sweep.
4. **UMAP** — 15 components, 35 neighbours, cosine metric.
5. **HDBSCAN** — `min_cluster_size=18`, `epsilon=0.1` → 110 micro-clusters, 18.5% noise.
6. **Noise reassignment** — noise points assigned to nearest medoid within cosine distance 0.35.
7. **Agglomerative merge** — 110 micro-clusters → 45 meta-clusters on medoid embeddings.
8. **Priority classifier** — XGBoost on raw embeddings + 14 urgency regex features; class-weighted. Test accuracy: 75% (high F1 0.80, medium F1 0.71, low F1 0.75).

---

## License

MIT
