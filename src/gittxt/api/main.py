import os
from fastapi import FastAPI
from gittxt.api.endpoints.inspect import router as inspect_router
from gittxt.api.endpoints.upload import router as upload_router
from gittxt.api.endpoints.scan import router as scan_router
from gittxt.api.endpoints.download import router as download_router
from gittxt.api.endpoints.summary import router as summary_router
from gittxt.api.endpoints.cleanup import router as cleanup_router

app = FastAPI(
    title="Gittxt API",
    description="API backend for Gittxt: scan, preview, and export GitHub repositories or local folders.",
    version="1.0.0"
)

# Ensure required directories exist at startup
required_dirs = ["/app/api/outputs", "/app/api/uploads"]
for directory in required_dirs:
    os.makedirs(directory, exist_ok=True)

# Register endpoints
app.include_router(inspect_router, tags=["Inspect"])
app.include_router(upload_router, tags=["Upload"])
app.include_router(scan_router, tags=["Scan"])
app.include_router(download_router, tags=["Download"])
app.include_router(summary_router, tags=["Summary"])
app.include_router(cleanup_router, tags=["Cleanup"])
