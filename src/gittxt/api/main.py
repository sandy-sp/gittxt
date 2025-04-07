import os
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import traceback

from gittxt import OUTPUT_DIR, __version__
from gittxt.core.logger import Logger
from gittxt.core.config import ConfigManager
from gittxt.api.endpoints import (
    inspect,
    upload,
    scan,
    download,
    summary,
    cleanup,
)

# Initialize logger for API
logger = Logger.get_logger(__name__)

# Load the config
config = ConfigManager.load_config()

# Define unified paths
UPLOAD_DIR = Path(config.get("upload_dir", OUTPUT_DIR / "uploads"))

app = FastAPI(
    title="Gittxt API",
    description="API backend for Gittxt: scan, preview, and export GitHub repositories or uploaded ZIPs.",
    version=__version__
)

# Enable CORS for frontend development (replace with specific domains in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure output/upload folders exist
startup_dirs = [OUTPUT_DIR, UPLOAD_DIR]
for d in startup_dirs:
    os.makedirs(d, exist_ok=True)
    logger.debug(f"Ensured directory exists: {d}")

# Register routers
app.include_router(inspect.router, tags=["Inspect"])
app.include_router(upload.router, tags=["Upload"])
app.include_router(scan.router, tags=["Scan"])
app.include_router(download.router, tags=["Download"])
app.include_router(summary.router, tags=["Summary"])
app.include_router(cleanup.router, tags=["Cleanup"])

# Health check endpoint
@app.get("/", tags=["Meta"])
async def healthcheck():
    """API health check endpoint"""
    logger.debug("Health check endpoint called")
    return {
        "status": "ok", 
        "message": "Gittxt API is running",
        "version": __version__
    }

# Custom exception handler
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """Custom exception handler with more detailed error responses"""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": str(exc.detail),
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handler for unexpected exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": f"An unexpected error occurred: {str(exc)}",
            "status_code": 500
        }
    )
