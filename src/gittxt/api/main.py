import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    description="API backend for Gittxt: scan, preview, and export GitHub repositories or local folders.",
    version="1.0.0"
)

# Optional: Allow cross-origin access for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure required directories exist at startup
required_dirs = ["/app/api/outputs", "/app/api/uploads"]
for directory in required_dirs:
    os.makedirs(directory, exist_ok=True)

# Register endpoints
app.include_router(inspect.router, tags=["Inspect"])
app.include_router(upload.router, tags=["Upload"])
app.include_router(scan.router, tags=["Scan"])
app.include_router(download.router, tags=["Download"])
app.include_router(summary.router, tags=["Summary"])
app.include_router(cleanup.router, tags=["Cleanup"])

# Optional healthcheck
@app.get("/", tags=["Meta"])
def healthcheck():
    return {"status": "ok", "message": "Gittxt API running"}
