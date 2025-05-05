tags_metadata = [
    {"name": "Scan", "description": "Persisted scans & artefacts"},
    {"name": "Inspect", "description": "Ephemeral, summary‑only view"},
]

from fastapi import APIRouter

api_router = APIRouter()
# ...existing router includes...
