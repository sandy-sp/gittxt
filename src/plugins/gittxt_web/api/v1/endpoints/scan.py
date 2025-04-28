from fastapi import APIRouter, HTTPException, status
from gittxt_web.api.v1.models.scan_models import ScanRequest, ScanResponse
from gittxt_web.core.services.scan_service import perform_scan
from gittxt_web.api.v1.models.response_models import ApiResponse

router = APIRouter(tags=["Scan"])

@router.post("/", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def scan_repo(request: ScanRequest):
    """
    Scan a GitHub/local repository and generate outputs (text, markdown, json, zip).
    """
    try:
        scan_result = await perform_scan(request)
        return ApiResponse(message="Scan completed successfully", data=scan_result.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
