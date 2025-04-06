from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from services.gittxt_runner import run_gittxt_inspect

router = APIRouter()

class InspectRequest(BaseModel):
    repo_url: str
    branch: Optional[str] = None
    subdir: Optional[str] = None

@router.post("/inspect")
async def inspect_repo(request: InspectRequest):
    try:
        result = run_gittxt_inspect(
            repo_url=request.repo_url,
            branch=request.branch,
            subdir=request.subdir
        )

        return JSONResponse(content={
            "repo_name": result["repo_name"],
            "branch": result["branch"],
            "tree": result["tree"],
            "textual_files": result["textual_files"],
            "non_textual_files": result["non_textual_files"],
            "summary": result["summary"],
            "preview_snippets": result["preview_snippets"]
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inspect failed: {str(e)}")
