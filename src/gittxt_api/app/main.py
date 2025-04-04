from fastapi import FastAPI
from mangum import Mangum
from gittxt_api.app.routes import scan
from gittxt_api.app.routes import scan, download

app = FastAPI(
    title="Gittxt API",
    description="API to scan GitHub repositories and generate AI-ready text outputs using Gittxt.",
    version="1.0.0"
)

# Include all route modules
app.include_router(scan.router)
app.include_router(download.router)

# Entry point for AWS Lambda via API Gateway
handler = Mangum(app)
