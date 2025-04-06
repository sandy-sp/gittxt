import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from gittxt import OUTPUT_DIR
from gittxt.api.endpoints import (
    inspect,
    upload,
    scan,
    download,
    summary,
    cleanup,
)

app = FastAPI(
    title="Gittxt API",
    description="API backend for Gittxt: scan, preview, and export GitHub repositories or uploaded ZIPs.",
    version="1.0.0"
)

# Enable CORS for frontend dev (replace with domains in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure output/upload folders exist
startup_dirs = [
    OUTPUT_DIR,
    Path("uploads")  # For uploaded ZIPs (used in /upload)
]
for d in startup_dirs:
    os.makedirs(d, exist_ok=True)

# Register routers
app.include_router(inspect.router, tags=["Inspect"])
app.include_router(upload.router, tags=["Upload"])
app.include_router(scan.router, tags=["Scan"])
app.include_router(download.router, tags=["Download"])
app.include_router(summary.router, tags=["Summary"])
app.include_router(cleanup.router, tags=["Cleanup"])

# Health check
@app.get("/", tags=["Meta"])
def healthcheck():
    return {"status": "ok", "message": "Gittxt API is running"}
