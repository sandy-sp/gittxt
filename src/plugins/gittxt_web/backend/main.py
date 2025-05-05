from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Pathimport RequestValidationError, HTTPException as StarletteHTTPException
import tomllib  # py3.11+, else import tomli as tomllib
from gittxt_web.api.v1 import api_router
from gittxt_web.settings import settings  # pydantic-based config
from gittxt import __version__api_router
from gittxt_web.api.v1.endpoints import scan, upload, summary, download, cleanup, inspect
# Load project metadata from pyproject.toml pydantic-based config
meta = tomllib.loads((Path(__file__).resolve().parents[2] / "pyproject.toml").read_text())["project"]

# Long-form description (Markdown)ject.toml
overview_md = (Path(__file__).parent / "docs" / "overview.md").read_text(encoding="utf-8")["project"]

app = FastAPI(scription (Markdown)
    title=meta["name"].replace("_", " ").title(),overview.md").read_text(encoding="utf-8")
    version=meta["version"],
    description=overview_md,
    contact=meta.get("authors", [{}])[0],title(),
    license_info=meta.get("license", {}),
    openapi_url="/openapi.json",
    docs_url="/docs","authors", [{}])[0],
    redoc_url="/redoc",et("license", {}),
)   openapi_url="/openapi.json",
    docs_url="/docs",
# CORS allow-list (env: FRONTEND_ORIGINS=...)
origins = [o.strip() for o in settings.FRONTEND_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,env: FRONTEND_ORIGINS=...)
    allow_origins=origins or ["http://localhost:5173"],.split(",") if o.strip()]
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,=origins or ["http://localhost:5173"],
)   allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
# Health check00,
@app.get("/health", tags=["Meta"])  # Add tags for Swagger
def health_check():
    return {"status": "ok", "version": __version__, "message": "Gittxt API is up"}
@app.get("/health", tags=["Meta"])
# Register all v1 routes
v1_prefix = "/v1"us": "ok", "version": __version__, "message": "Gittxt API is up"}
app.include_router(scan.router, prefix=f"{v1_prefix}/scan")
app.include_router(upload.router, prefix=f"{v1_prefix}/upload")
app.include_router(summary.router, prefix=f"{v1_prefix}/summary")
app.include_router(download.router, prefix=f"{v1_prefix}/download")
app.include_router(cleanup.router, prefix=f"{v1_prefix}/cleanup")
app.include_router(inspect.router, prefix=f"{v1_prefix}/inspect")  # Register the router

# Exception: HTTP
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            detail=str(exc.detail),
        ).dict()
    )

# Exception: Validation
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="Validation Error",
            detail=str(exc.errors()),
        ).dict()
    )
# Include API routerapp.include_router(api_router)