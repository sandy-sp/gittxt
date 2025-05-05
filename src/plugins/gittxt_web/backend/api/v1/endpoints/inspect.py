from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl, Field
from gittxt_web.core.services.scan_service import perform_scan
from gittxt_web.core.models.scan_models import ScanRequest  # Ensure this is imported

router = APIRouter(tags=["Inspect"])

class InspectRequest(BaseModel):
    repo_url: HttpUrl

class InspectResp(BaseModel):
    summary: dict = Field(
        example={
            "total_tokens": 12345,
            "total_files": 42,
            "language_breakdown": {"Python": 30, "Markdown": 12},
        }
    )

@router.post("/", response_model=InspectResp,
             summary="Stateless scan returning only summary",
             responses={200: {"model": InspectResp, "description": "Successful Response"}},
             tags=["Inspect"])
async def inspect_repo(req: InspectRequest):
    """
    Perform a stateless scan and return a summary without persisting artifacts.
    """
    try:
        req_model = ScanRequest(repo_url=req.repo_url)  # Create ScanRequest
        result = await perform_scan(req_model, persist=False)  # Pass ScanRequest
        return {"summary": result.summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
