from fastapi import FastAPI, RequestValidationError, HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import tomllib  # py3.11+, else import tomli as tomllib
from fastapi.responses import JSONResponse
from gittxt_web.backend.api.v1 import api_router
from gittxt_web.backend.settings import settings  # pydantic-based config
from gittxt import __version__
from gittxt_web.backend.api.v1.endpoints import scan, upload, summary, download, cleanup, inspect
from gittxt_web.backend.api.v1.models.error_models import ErrorResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# Load project metadata from pyproject.toml
meta = tomllib.loads((Path(__file__).resolve().parents[2] / "pyproject.toml").read_text())

# Long-form description (Markdown)
overview_md = (Path(__file__).resolve().parents[2] / "docs" / "about.md").read_text(encoding="utf-8")

app = FastAPI(
    title=meta["project"]["name"].replace("_", " ").title(),
    version=meta["project"]["version"],
    description=overview_md,
    contact=meta["project"].get("authors", [{}])[0],
    license_info=meta["project"].get("license", {}),
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS allow-list (env: FRONTEND_ORIGINS=Ellipsis)
origins = [o.strip() for o in settings.FRONTEND_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["http://localhost:5173"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,
)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    response = await limiter(request, call_next)
    return response

# Add HTTPS redirect middleware
app.add_middleware(HTTPSRedirectMiddleware)

# Health check
@app.get("/health", tags=["Meta"])
@limiter.limit("5/minute")
def health_check():
    return {"status": "ok", "version": __version__, "message": "Gittxt API is up"}

# Register all v1 routes
v1_prefix = "/v1"
app.include_router(scan.router, prefix=f"{v1_prefix}/scan")
app.include_router(upload.router, prefix=f"{v1_prefix}/upload")
app.include_router(summary.router, prefix=f"{v1_prefix}/summary")
app.include_router(download.router, prefix=f"{v1_prefix}/download")
app.include_router(cleanup.router, prefix=f"{v1_prefix}/cleanup")
app.include_router(inspect.router, prefix=f"{v1_prefix}/inspect")

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