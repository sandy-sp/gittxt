import os
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from gittxt import OUTPUT_DIR, __version__
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

# Health check endpoint
@app.get("/", tags=["Meta"])
async def healthcheck():
    """API health check endpoint"""
    return {
        "status": "ok", 
        "message": "Gittxt API is running",
        "version": __version__
    }

# Custom exception handler
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """Custom exception handler with more detailed error responses"""
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
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": f"An unexpected error occurred: {str(exc)}",
            "status_code": 500
        }
    )
