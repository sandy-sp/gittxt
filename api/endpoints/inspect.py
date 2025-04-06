from fastapi import APIRouter, HTTPException
from services.gittxt_runner import run_gittxt_inspect
from schemas.inspect import InspectRequest, InspectResponse, PreviewSnippet

router = APIRouter()

@router.post("/inspect", response_model=InspectResponse)
async def inspect_repo(request: InspectRequest):
    try:
        result = run_gittxt_inspect(
            repo_url=request.repo_url,
            branch=request.branch,
            subdir=request.subdir
        )

        return InspectResponse(
            repo_name=result["repo_name"],
            branch=result["branch"],
            tree=result.get("tree", []),
            textual_files=result.get("textual_files", []),
            non_textual_files=result.get("non_textual_files", []),
            summary=result.get("summary", {}),
            preview_snippets=[
                PreviewSnippet(path=k, preview=v)
                for k, v in result.get("preview_snippets", {}).items()
            ]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inspect failed: {str(e)}")
