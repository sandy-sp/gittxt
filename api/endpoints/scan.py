from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
from services.gittxt_runner import run_gittxt_scan

router = APIRouter()

class ScanRequest(BaseModel):
    repo_url: str
    branch: Optional[str] = None
    subdir: Optional[str] = None
    exclude_dirs: Optional[List[str]] = []
    include_patterns: Optional[List[str]] = []
    exclude_patterns: Optional[List[str]] = []
    size_limit: Optional[int] = None
    tree_depth: Optional[int] = None
    lite: Optional[bool] = False

@router.post("/scan")
async def scan_repo(request: ScanRequest):
    try:
        result = run_gittxt_scan(
            repo_url=request.repo_url,
            options={
                "branch": request.branch,
                "subdir": request.subdir,
                "exclude_dirs": request.exclude_dirs,
                "include_patterns": request.include_patterns,
                "exclude_patterns": request.exclude_patterns,
                "size_limit": request.size_limit,
                "tree_depth": request.tree_depth,
                "lite": request.lite
            }
        )

        scan_id = result["scan_id"]
        base_url = f"/download/{scan_id}"
        outputs = result["outputs"]

        return JSONResponse(content={
            "scan_id": scan_id,
            "repo_name": result["repo_name"],
            "branch": result["branch"],
            "summary": result["summary"],
            "download_urls": {
                "txt": f"{base_url}?format=txt" if outputs.get("txt") else None,
                "md": f"{base_url}?format=md" if outputs.get("md") else None,
                "json": f"{base_url}?format=json" if outputs.get("json") else None,
                "zip": f"{base_url}?format=zip" if outputs.get("zip") else None,
            }
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")
