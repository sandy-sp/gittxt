from fastapi import APIRouter, HTTPException, status
from gittxt_api.api.v1.models.inspect_models import InspectRequest, InspectResponse
from gittxt_api.core.services.inspect_service import perform_inspect
from gittxt_api.api.v1.models.response_models import ApiResponse

router = APIRouter(tags=["Inspect"])

@router.post("/", response_model=InspectResponse, status_code=status.HTTP_200_OK)
async def inspect_repo(request: InspectRequest):
    """
    Pre-scan endpoint to classify files and return directory tree (no output generated).
    """
    try:
        inspect_result = await perform_inspect(request)
        return ApiResponse(message="Inspect successful", data=inspect_result.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
