from fastapi import APIRouter, HTTPException, Request
from services.gittxt_runner import run_gittxt_scan
from schemas.scan import ScanRequest, ScanResponse, DownloadURLs

router = APIRouter()

@router.post("/scan", response_model=ScanResponse)
async def scan_repo(request: Request, payload: ScanRequest):
    try:
        result = run_gittxt_scan(
            repo_url=payload.repo_url,
            options={
                "branch": payload.branch,
                "subdir": payload.subdir,
                "exclude_dirs": payload.exclude_dirs,
                "include_patterns": payload.include_patterns,
                "exclude_patterns": payload.exclude_patterns,
                "size_limit": payload.size_limit,
                "tree_depth": payload.tree_depth,
                "lite": payload.lite
            }
        )

        scan_id = result["scan_id"]
        base_url = str(request.base_url).rstrip("/") + f"/download/{scan_id}"
        outputs = result["outputs"]

        return ScanResponse(
            scan_id=scan_id,
            repo_name=result["repo_name"],
            branch=result["branch"],
            summary=result["summary"],
            download_urls=DownloadURLs(
                txt=f"{base_url}?format=txt" if outputs.get("txt") else None,
                md=f"{base_url}?format=md" if outputs.get("md") else None,
                json=f"{base_url}?format=json" if outputs.get("json") else None,
                zip=f"{base_url}?format=zip" if outputs.get("zip") else None,
            )
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")
