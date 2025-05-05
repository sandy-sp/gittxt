from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl, Field, ValidationError
from gittxt_web.core.services.scan_service import perform_scan
from gittxt_web.api.v1.models.scan_models import ScanRequest

router = APIRouter(tags=["Inspect"])

class InspectRequest(BaseModel):
    repo_url: HttpUrl = Field(
        ..., description="HTTPS URL of a public GitHub repository",
        example="https://github.com/openai/tiktoken"
    )

class InspectResp(BaseModel):
    summary: dict = Field(
        example={
            "total_tokens": 12345,
            "total_files": 42,
            "language_breakdown": {"Python": 30, "Markdown": 12},
        }
    )

@router.post(
    "/", response_model=InspectResp,
    summary="Stateless scan returning only summary",
    responses={
        200: {"model": InspectResp, "description": "Successful Response"},
        400: {"description": "Invalid GitHub URL"},
        500: {"description": "Internal Server Error"},
    },
    tags=["Inspect"]
)
async def inspect_repo(req: InspectRequest):
    """
    Perform a stateless scan and return a summary without persisting artifacts.
    """
    try:
        # Validate GitHub URL
        if not req.repo_url.startswith("https://github.com/"):
            raise HTTPException(status_code=400, detail="Invalid GitHub URL. Must start with 'https://github.com/'.")

        # Create ScanRequest model
        req_model = ScanRequest(repo_url=req.repo_url)

        # Perform scan
        result = await perform_scan(req_model, persist=False)

        return {"summary": result.summary}
    except ValidationError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
