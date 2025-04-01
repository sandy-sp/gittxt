from fastapi import APIRouter, HTTPException
from gittxt_api.models.scan import ScanRequest, ScanResponse

router = APIRouter()

@router.post("/", response_model=ScanResponse)
async def scan_repo(request: ScanRequest):
    # Placeholder for calling the scan service
    raise HTTPException(status_code=501, detail="Scan logic not implemented yet")
