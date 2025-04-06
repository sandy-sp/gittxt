from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
import logging
from pathlib import Path
import uuid
from gittxt.api.services.gittxt_runner import run_gittxt_scan, GittxtRunnerError
from gittxt.api.schemas.scan import ScanRequest, ScanResponse, DownloadURLs

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/scan", response_model=ScanResponse, tags=["Scan"])
async def start_scan(request: Request, payload: ScanRequest, background_tasks: BackgroundTasks):
    """
    Initiate a Gittxt scan on a repository.

    Args:
        payload (ScanRequest): Contains repository details and scan options.

    Returns:
        ScanResponse: Scan results including download URLs.
    """
    logger.info(f"Received scan request for repo_path: {payload.repo_path}, branch: {payload.branch}")

    try:
        scan_id = str(uuid.uuid4())
        repo_path = Path(payload.repo_path)

        if not repo_path.exists() or not repo_path.is_dir():
            logger.warning(f"Invalid repository path: {payload.repo_path}")
            raise HTTPException(status_code=400, detail="Invalid repository path.")

        result = await run_gittxt_scan(
            repo_path=repo_path,
            options={
                "branch": payload.branch,
                "subdir": payload.subdir,
                "exclude_dirs": payload.exclude_dirs,
                "include_patterns": payload.include_patterns,
                "exclude_patterns": payload.exclude_patterns,
                "size_limit": payload.size_limit,
                "tree_depth": payload.tree_depth,
                "lite": payload.lite,
            },
            scan_id=scan_id,
            background_tasks=background_tasks
        )

        base_url = str(request.base_url).rstrip("/") + f"/download/{scan_id}"
        outputs = result["outputs"]

        logger.info(f"Scan completed for repo_path: {payload.repo_path}, scan_id: {scan_id}")

        return ScanResponse(
            scan_id=scan_id,
            repo_name=result.get("repo_name"),
            branch=result.get("branch", "main"),
            summary=result.get("summary", {}),
            download_urls=DownloadURLs(
                txt=f"{base_url}?format=txt" if outputs.get("txt") else None,
                md=f"{base_url}?format=md" if outputs.get("md") else None,
                json=f"{base_url}?format=json" if outputs.get("json") else None,
                zip=f"{base_url}?format=zip" if outputs.get("zip") else None,
            ),
        )

    except GittxtRunnerError as runner_exc:
        logger.error(f"Gittxt Runner Error for {payload.repo_path}: {runner_exc}", exc_info=True)
        raise HTTPException(status_code=runner_exc.status_code, detail=str(runner_exc))
    except Exception as e:
        logger.error(f"Unexpected error initiating scan for {payload.repo_path}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")
