# src/gittxt-ui/backend/app.py

from fastapi import FastAPI
from .api.config_endpoints import router as config_router
from .api.scans_endpoints import router as scans_router
from .api.artifacts_endpoints import router as artifacts_router
from .api.ws_progress_endpoints import router as ws_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="Gittxt FastAPI Backend",
        version="1.0.0",
        description="A backend that wraps Gittxt scanning with real-time progress and config endpoints.",
    )

    # Include routers
    app.include_router(config_router, prefix="/config", tags=["config"])
    app.include_router(scans_router, prefix="/scans", tags=["scans"])
    app.include_router(artifacts_router, prefix="/artifacts", tags=["artifacts"])
    app.include_router(ws_router, prefix="/wsprogress", tags=["ws-progress"])

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
