# src/gittxt_api/main.py
import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.gittxt_api.api import scan, health

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(name)s: %(message)s"
)

app = FastAPI(
    title="Gittxt API",
    description="FastAPI backend for scanning GitHub repos using Gittxt",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(scan.router, prefix="/scan", tags=["Scan"])

# Mount UI static and template routes
app.mount("/static", StaticFiles(directory="src/gittxt_api/ui/static"), name="static")
templates = Jinja2Templates(directory="src/gittxt_api/ui/templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
