from fastapi import APIRouter, HTTPException, Path
import shutil
import pathlib
from gittxt.api.dependencies import OUTPUT_DIR

router = APIRouter(tags=["Cleanup"])

@router.delete("/{scan_id}")
async def cleanup_scan(scan_id: str = Path(..., description="Scan ID to delete")):
    scan_path = OUTPUT_DIR / scan_id
    if not scan_path.exists():
        raise HTTPException(status_code=404, detail="Scan ID not found")

    try:
        shutil.rmtree(scan_path, ignore_errors=True)
        return {"status": "ok", "message": f"Deleted scan ID: {scan_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete: {e}")
