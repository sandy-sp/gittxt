from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from gittxt import __version__

from gittxt.api.routers import inspect, scan, upload, summary, download, cleanup

app = FastAPI(
    title="Gittxt API",
    description="Scan GitHub repos and generate AI-ready outputs.",
    version=__version__,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Meta"])
def health_check():
    return {"status": "ok", "version": __version__, "message": "API is up"}

# Register routers
app.include_router(inspect.router, prefix="/inspect")
app.include_router(scan.router, prefix="/scan")
app.include_router(upload.router, prefix="/upload")
app.include_router(summary.router, prefix="/summary")
app.include_router(download.router, prefix="/download")
app.include_router(cleanup.router, prefix="/cleanup")
