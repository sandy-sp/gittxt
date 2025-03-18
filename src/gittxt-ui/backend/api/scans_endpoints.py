# src/gittxt-ui/backend/api/scans_endpoints.py

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from core.scanning_service import SCANS, run_scan_task, update_scan_progress
import uuid

router = APIRouter()

class ScanRequest(BaseModel):
    repo_url: str
    file_types: str = "code,docs"
    output_format: str = "txt,json"
    # Add more if needed (include_patterns, exclude_patterns, size_limit, etc.)

@router.post("/")
async def start_scan(req: ScanRequest, background_tasks: BackgroundTasks):
    """
    Initiate a Gittxt scan in the background. Returns a scan_id immediately.
    The frontend can poll or use SSE/WebSockets to get real-time progress.
    """
    scan_id = str(uuid.uuid4())
    # Initialize the global store entry for this scan
    SCANS[scan_id] = {
        "status": "queued",
        "progress": 0,
        "current_file": "",
        "error": None
    }

    # Schedule the async scanning task
    background_tasks.add_task(
        run_scan_task,
        scan_id,
        req.repo_url,
        req.file_types,
        req.output_format,
        update_scan_progress
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
