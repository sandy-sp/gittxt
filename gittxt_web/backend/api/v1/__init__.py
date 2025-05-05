tags_metadata = [
    {"name": "Scan", "description": "Persisted scans & artefacts"},
    {"name": "Inspect", "description": "Ephemeral, summary‑only view"},
]

from fastapi import APIRouter
from .endpoints import scan, upload, summary, download, cleanup, inspect

api_router = APIRouter()
api_router.include_router(scan.router, prefix="/scan")
api_router.include_router(upload.router, prefix="/upload")
api_router.include_router(summary.router, prefix="/summary")
api_router.include_router(download.router, prefix="/download")
api_router.include_router(cleanup.router, prefix="/cleanup")
api_router.include_router(inspect.router, prefix="/inspect")
