# gittxt-api/app.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config_endpoints import router as config_router
from api.scans_endpoints import router as scans_router
from api.artifacts_endpoints import router as artifacts_router
from api.ws_progress_endpoints import router as ws_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="Gittxt FastAPI Backend",
        version="1.0.0",
        description="A FastAPI backend to power Gittxt API for AI-ready repo scanning.",
    )

    # Optional: Open CORS policy for frontend (adjust as needed)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount all routers
    app.include_router(config_router, prefix="/config", tags=["Config"])
    app.include_router(scans_router, prefix="/scans", tags=["Scans"])
    app.include_router(artifacts_router, prefix="/artifacts", tags=["Artifacts"])
    app.include_router(ws_router, prefix="/wsprogress", tags=["WebSocket"])

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
