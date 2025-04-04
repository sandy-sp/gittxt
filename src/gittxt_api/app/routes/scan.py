from fastapi import APIRouter, HTTPException
from uuid import uuid4

from gittxt_api.app.models.request import ScanRequest
from gittxt_api.app.models.response import ScanResponse, ErrorResponse
from gittxt_api.app.services.scan_service import run_scan_job

router = APIRouter()


@router.post(
    "/scan",
    response_model=ScanResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["Scan"]
)
async def scan_repo(request: ScanRequest):
    try:
        # Generate a unique scan ID for temp paths, zip names, etc.
        scan_id = str(uuid4())

        # Run the scan job (delegated to service layer)
        result = await run_scan_job(request, scan_id)

        if not result:
            raise HTTPException(status_code=400, detail="Scan failed or repository could not be processed.")

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
