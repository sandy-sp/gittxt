from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, HttpUrl, Field
from gittxt_web.core.services.scan_service import perform_scan

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
        result = await perform_scan(
            repo_path=req.repo_url,
            persist=False  # Ensure no artifacts are saved
        )
        return {"summary": result.summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
