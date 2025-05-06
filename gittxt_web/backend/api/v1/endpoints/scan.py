from fastapi import APIRouter, HTTPException, status
from gittxt_web.backend.api.v1.models.scan_models import ScanRequest, ScanStartResp
from gittxt_web.backend.core.services.scan_service import perform_scan

router = APIRouter(tags=["Scan"])

@router.post("/", response_model=ScanStartResp, status_code=201,
             summary="Kick off a persistent scan",
             responses={
                 201: {"description": "Scan scheduled"},
                 400: {"description": "Invalid Git URL"},
                 500: {"description": "Internal error"},
             })
async def start_scan(req: ScanRequest):
    """
    Scan a GitHub/local repository and generate outputs (text, markdown, json, zip).
    """
    try:
        scan_result = await perform_scan(req)
        return ScanStartResp(message="Scan scheduled successfully", data=scan_result.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
