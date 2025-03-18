# src/gittxt-ui/backend/api/scans_endpoints.py

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from core.scanning_service import (
    SCANS,
    run_scan_task,
    update_scan_progress,
    build_directory_tree,
    gather_file_extensions,  # We'll define or reference this in scanning_service.py
    remove_ephemeral_outputs,  # We'll define or reference a new helper for removing outputs
)
import uuid
from typing import List, Optional
from pathlib import Path
from gittxt.repository import RepositoryHandler
from gittxt.utils.cleanup_utils import cleanup_temp_folder

router = APIRouter()

class TreeRequest(BaseModel):
    repo_url: str
    branch: str | None = None

@router.post("/tree")
async def get_repo_tree(req: TreeRequest):
    """
    1) Clones the remote repo or verifies a local path (via RepositoryHandler).
    2) Builds and returns the directory structure in JSON.
    3) Also returns a list of distinct file extensions found (dynamic file types).
    4) Cleans up the cloned repo folder if it's remote.
    """
    try:
        repo_handler = RepositoryHandler(source=req.repo_url, branch=req.branch)
        repo_path, subdir, is_remote = repo_handler.get_local_path()

        if not repo_path:
            raise HTTPException(status_code=400, detail="Invalid repository path.")

        scan_root = Path(repo_path)
        if subdir:
            scan_root = scan_root / subdir

        # Build the tree data
        tree_data = build_directory_tree(scan_root)

        # Gather file extensions => for "Better UI for file types"
        ext_map = gather_file_extensions(scan_root)
        distinct_exts = sorted(ext_map.keys())

        # If remote, remove the repo folder now, because we're just doing "tree" pre-scan
        if is_remote:
            cleanup_temp_folder(Path(repo_path))

        return {
            "success": True,
            "tree": tree_data,
            "file_extensions": distinct_exts,
        }
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
    The frontend can track progress via the WebSocket endpoint only.
    """
    scan_id = str(uuid.uuid4())
    # Initialize store entry
    SCANS[scan_id] = {
        "status": "queued",
        "progress": 0,
        "current_file": "",
        "error": None,
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
        req.branch,
    )

    return {
        "scan_id": scan_id,
        "status": "queued",
        "message": "Scan scheduled.",
    }

@router.get("/{scan_id}")
def get_scan_info(scan_id: str):
    """
    Retrieve info about a particular scan (status, progress, final results).
    Typically, your front-end might rely on WebSockets now instead of polling,
    but this is still useful for quick info.
    """
    info = SCANS.get(scan_id)
    if not info:
        raise HTTPException(status_code=404, detail="Scan not found")
    return info

@router.delete("/{scan_id}/close")
def close_scan_session(scan_id: str):
    """
    Clean up ephemeral output/artifacts and remove scan data from SCANS dict.
    The front-end calls this endpoint when the user ends the scanning session,
    e.g. going back to home page or starting a new scan. The user can also
    call it explicitly if they no longer need the artifacts.
    """
    info = SCANS.get(scan_id)
    if not info:
        raise HTTPException(status_code=404, detail="Scan not found or already removed.")

    # If the scan already created ephemeral outputs, remove them
    output_dir = info.get("output_dir")
    if output_dir:
        remove_ephemeral_outputs(Path(output_dir))

    # Remove from SCANS dictionary
    SCANS.pop(scan_id, None)

    return {"success": True, "message": f"Scan session {scan_id} cleaned up."}
