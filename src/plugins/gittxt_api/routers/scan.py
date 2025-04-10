from fastapi import APIRouter, HTTPException
from plugins.gittxt_api.models.scan_models import ScanRequest, ScanResponse
from plugins.gittxt_api.services.scan_service import perform_scan

router = APIRouter(tags=["Scan"])

@router.post("/", response_model=ScanResponse)
async def scan_repo(request: ScanRequest):
    try:
        return await perform_scan(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
