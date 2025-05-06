from fastapi import APIRouter, HTTPException, Path, status
import shutil
from gittxt_web.backend.api.v1.deps import get_output_dir
from gittxt_web.backend.api.v1.models.response_models import ApiResponse

router = APIRouter(tags=["Cleanup"])

@router.delete("/{scan_id}", response_model=ApiResponse, status_code=status.HTTP_200_OK)
async def cleanup_scan(scan_id: str = Path(Ellipsis, description="Scan ID to delete")):
    """
    Permanently delete all output artifacts for a given scan ID.
    """
    output_dir = get_output_dir()
    target_path = output_dir / scan_id

    if not target_path.exists():
        raise HTTPException(status_code=404, detail="Scan ID not found.")

    try:
        shutil.rmtree(target_path, ignore_errors=True)
        return ApiResponse(message=f"Deleted scan ID: {scan_id}", data={"scan_id": scan_id})    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete: {e}")
