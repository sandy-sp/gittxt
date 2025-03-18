# src/gittxt-ui/backend/api/scans_endpoints.py

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from core.scanning_service import SCANS, run_scan_task, update_scan_progress, build_directory_tree
import uuid
from typing import List, Optional
from pathlib import Path
import shutil
from gittxt.repository import RepositoryHandler
from gittxt.utils.cleanup_utils import cleanup_temp_folder

router = APIRouter()

class TreeRequest(BaseModel):
    repo_url: str
    branch: str | None = None

@router.post("/tree")
async def get_repo_tree(req: TreeRequest):
    """
    1) If remote, clone the repo shallowly (via RepositoryHandler).
    2) Build and return the directory structure in JSON.
    3) Optional: store a temp folder so user can reuse the same path next step.
    """
    try:
        repo_handler = RepositoryHandler(source=req.repo_url, branch=req.branch)
        repo_path, subdir, is_remote = repo_handler.get_local_path()

        if not repo_path:
            raise HTTPException(status_code=400, detail="Invalid repository path.")

        scan_root = Path(repo_path)
        if subdir:
            scan_root = scan_root / subdir

        # Build the tree
        tree_data = build_directory_tree(scan_root)
        # If remote, you might keep it around in memory or stash path in a short-lived store
        # so the next request can skip recloning. For demonstration, we just remove it now.
        if is_remote:
            cleanup_temp_folder(Path(repo_path))

        return {"success": True, "tree": tree_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class ScanRequest(BaseModel):
    repo_url: str
    file_types: str = "code,docs"
    output_format: str = "txt,json"
    include_patterns: List[str] = []
    exclude_patterns: List[str] = [".git", "node_modules"]
    size_limit: Optional[int] = None
    branch: Optional[str] = None

@router.post("/")
async def start_scan(req: ScanRequest, background_tasks: BackgroundTasks):
    """
    Initiate a Gittxt scan in the background. Returns a scan_id immediately.
    The frontend can poll or use WebSockets to get real-time progress.
    """
    scan_id = str(uuid.uuid4())
    # Initialize store entry
    SCANS[scan_id] = {
        "status": "queued",
        "progress": 0,
        "current_file": "",
        "error": None
    }

    # Convert file_types from a comma-separated string to a list
    ft_list = [ft.strip().lower() for ft in req.file_types.split(",") if ft.strip()]

    background_tasks.add_task(
        run_scan_task,
        scan_id,
        req.repo_url,
        ft_list,
        req.output_format,
        update_scan_progress,
        req.include_patterns,
        req.exclude_patterns,
        req.size_limit,
        req.branch
    )

    return {
        "scan_id": scan_id,
        "status": "queued",
        "message": "Scan scheduled"
    }

@router.get("/{scan_id}")
def get_scan_info(scan_id: str):
    """
    Retrieve info about a particular scan (status, progress, final results).
    """
    info = SCANS.get(scan_id)
    if not info:
        raise HTTPException(status_code=404, detail="Scan not found")
    return info
