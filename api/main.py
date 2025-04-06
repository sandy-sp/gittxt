from fastapi import FastAPI
from endpoints.scan import router as scan_router
from endpoints.download import router as download_router

app = FastAPI(title="Gittxt API", version="1.0")

app.include_router(scan_router, prefix="/scan", tags=["Scan"])
app.include_router(download_router, prefix="/download", tags=["Download"])
