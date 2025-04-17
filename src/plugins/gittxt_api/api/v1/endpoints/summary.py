from fastapi import APIRouter, HTTPException, Path, status
from gittxt_api.core.utils.json_utils import load_json_summary
from gittxt_api.api.v1.deps import get_output_dir
from gittxt_api.api.v1.models.response_models import ApiResponse

router = APIRouter(tags=["Summary"])

@router.get("/{scan_id}", status_code=status.HTTP_200_OK)
async def get_summary(scan_id: str = Path(..., description="Scan ID of completed scan job")):
    """
    Fetch the JSON summary of a completed scan.
    """
    try:
        summary_dir = get_output_dir() / scan_id / "json"
        summary_data = await load_json_summary(summary_dir)
        return ApiResponse(message="Summary loaded", data=summary_data)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
