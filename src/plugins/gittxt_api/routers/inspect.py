from fastapi import APIRouter, HTTPException
from plugins.gittxt_api.models.inspect_models import InspectRequest
from plugins.gittxt_api.services.inspect_service import perform_inspect

router = APIRouter(tags=["Inspect"])

@router.post("/")
async def inspect_repo(request: InspectRequest):
    try:
        result = await perform_inspect(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
