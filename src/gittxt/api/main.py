import os
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from gittxt import OUTPUT_DIR
from gittxt.api.endpoints import (
    inspect,
    upload,
    scan,
    download,
    summary,  # Add summary endpoint
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
app.include_router(summary.router, tags=["Summary"])  # Include summary router
app.include_router(cleanup.router, tags=["Cleanup"])

# Root endpoint
@app.get("/", tags=["General"])
async def read_root():
    return {"message": "Welcome to the Gittxt API"}

# Custom exception handler
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
