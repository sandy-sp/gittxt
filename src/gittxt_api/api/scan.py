from fastapi import APIRouter, HTTPException
from gittxt_api.models.scan import ScanRequest, ScanResponse
from gittxt_api.services.scan_service import scan_repo_logic

router = APIRouter()

@router.post("/", response_model=ScanResponse)
async def scan_repo(request: ScanRequest):
    try:
        result = await scan_repo_logic(request)
        return ScanResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
