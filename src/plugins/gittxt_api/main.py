from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from gittxt import __version__

# Import all routers
from gittxt_api.api.v1.endpoints import (
    scan,
    inspect,
    upload,
    summary,
    download,
    cleanup,
)
from gittxt_api.api.v1.models.response_models import ErrorResponse
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI(
    title="Gittxt API",
    description="Scan GitHub repos and generate AI-ready outputs.",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS config — replace with allowed domains in prod
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: restrict this!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health", tags=["Meta"])
def health_check():
    return {"status": "ok", "version": __version__, "message": "API is up"}

# Register all v1 routes
v1_prefix = "/v1"
app.include_router(scan.router, prefix=f"{v1_prefix}/scan")
app.include_router(inspect.router, prefix=f"{v1_prefix}/inspect")
app.include_router(upload.router, prefix=f"{v1_prefix}/upload")
app.include_router(summary.router, prefix=f"{v1_prefix}/summary")
app.include_router(download.router, prefix=f"{v1_prefix}/download")
app.include_router(cleanup.router, prefix=f"{v1_prefix}/cleanup")

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
