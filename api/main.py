from fastapi import FastAPI
from endpoints.inspect import router as inspect_router
from endpoints.upload import router as upload_router
from endpoints.scan import router as scan_router
from endpoints.download import router as download_router
from endpoints.summary import router as summary_router
from endpoints.cleanup import router as cleanup_router

app = FastAPI(
    title="Gittxt API",
    description="API backend for Gittxt: scan, preview, and export GitHub repositories or local folders.",
    version="1.0.0"
)

# Register endpoints
app.include_router(inspect_router, tags=["Inspect"])
app.include_router(upload_router, tags=["Upload"])
app.include_router(scan_router, tags=["Scan"])
app.include_router(download_router, tags=["Download"])
app.include_router(summary_router, tags=["Summary"])
app.include_router(cleanup_router, tags=["Cleanup"])
