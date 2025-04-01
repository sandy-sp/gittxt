from fastapi import FastAPI
from .api.routes import router as api_router

app = FastAPI(title="Gittxt API", version="1.6.0")
app.include_router(api_router)
