from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from gittxt import __version__
from gittxt.core.logger import Logger
from gittxt.core.config import ConfigManager

# Import routers from the endpoints sub-package
from gittxt.api.endpoints.inspect import router as inspect_router
from gittxt.api.endpoints.scan import router as scan_router
from gittxt.api.endpoints.download import router as download_router
from gittxt.api.endpoints.summary import router as summary_router
from gittxt.api.endpoints.cleanup import router as cleanup_router
from gittxt.api.endpoints.upload import router as upload_router

logger = Logger.get_logger(__name__)
config = ConfigManager.load_config()

app = FastAPI(
    title="Gittxt API",
    description="API that calls Gittxt core modules (endpoints in separate files).",
    version=__version__,
)

# (Optional) CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic "health" or "root" endpoint
@app.get("/health", tags=["Meta"])
def health_check():
    return {
        "status": "ok",
        "version": __version__,
        "message": "Gittxt API is running"
    }

# Include our sub-routers
app.include_router(inspect_router)
app.include_router(scan_router)
app.include_router(download_router)
app.include_router(summary_router)
app.include_router(cleanup_router)
app.include_router(upload_router)
