from fastapi import APIRouter, BackgroundTasks, HTTPException
from gittxt_api.schemas.scan_schemas import ScanRequest, TreeRequest
from gittxt_api.core.scanning_service import (
    SCANS,
    run_scan_task,
    update_scan_progress
)
from gittxt_api.services.tree_service import (
    build_directory_tree,
    gather_file_extensions,
    remove_ephemeral_outputs
)
from gittxt.repository import RepositoryHandler
from gittxt.utils.cleanup_utils import cleanup_temp_folder
from pathlib import Path
import uuid

router = APIRouter()

@router.post("/tree")
async def get_repo_tree(req: TreeRequest):
    """
    Generates directory tree and extension map from a GitHub/local repo.
    """
    try:
        repo_handler = RepositoryHandler(source=req.repo_url, branch=req.branch)
        repo_path, subdir, is_remote, _ = repo_handler.get_local_path()

        if not repo_path:
            raise HTTPException(status_code=400, detail="Invalid repository path.")

        scan_root = Path(repo_path)
        if subdir:
            scan_root = scan_root / subdir

        tree_data = build_directory_tree(scan_root)
        ext_map = gather_file_extensions(scan_root)

        if is_remote:
            cleanup_temp_folder(Path(repo_path))

        return {
            "success": True,
            "tree": tree_data,
            "file_extensions": sorted(ext_map.keys()),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/")
async def start_scan(req: ScanRequest, background_tasks: BackgroundTasks):
    """
    Launch a Gittxt scan asynchronously.
    """
    scan_id = str(uuid.uuid4())

    SCANS[scan_id] = {
        "status": "queued",
        "progress": 0,
        "current_file": "",
        "error": None,
    }

    background_tasks.add_task(
        run_scan_task,
        scan_id,
        req.repo_url,
        req.file_types,
        req.output_format,
        update_scan_progress,
        req.include_patterns,
        req.exclude_patterns,
        req.size_limit,
        req.branch,
        req.tree_depth,
        req.create_zip
    )

    return {"scan_id": scan_id, "status": "queued", "message": "Scan scheduled."}


@router.get("/{scan_id}")
def get_scan_info(scan_id: str):
    """Fetch status & metadata of a running or completed scan."""
    info = SCANS.get(scan_id)
    if not info:
        raise HTTPException(status_code=404, detail="Scan not found")

    response = info.copy()

    if info.get("status") == "done":
        response["artifacts"] = {
            "txt": f"/artifacts/{scan_id}/txt",
            "json": f"/artifacts/{scan_id}/json",
            "md": f"/artifacts/{scan_id}/md",
            "zip": f"/artifacts/{scan_id}/zip"
        }

    return response


@router.delete("/{scan_id}/close")
def close_scan_session(scan_id: str):
    """Cleanup ephemeral artifacts and session state."""
    info = SCANS.get(scan_id)
    if not info:
        raise HTTPException(status_code=404, detail="Scan not found or already removed.")

    output_dir = info.get("output_dir")
    if output_dir:
        remove_ephemeral_outputs(Path(output_dir))

    SCANS.pop(scan_id, None)

    return {"success": True, "message": f"Scan session {scan_id} cleaned up."}
