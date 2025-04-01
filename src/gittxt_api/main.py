from fastapi import FastAPI
from gittxt_api.api import scan, download, health

app = FastAPI(
    title="Gittxt API",
    description="FastAPI backend for scanning GitHub repos using Gittxt",
    version="1.0.0"
)

app.include_router(scan.router, prefix="/scan", tags=["Scanner"])
app.include_router(download.router, prefix="/download", tags=["Download"])
app.include_router(health.router, prefix="/health")
