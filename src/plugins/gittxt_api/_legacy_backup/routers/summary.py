from fastapi import APIRouter, HTTPException, Path
from plugins.gittxt_api.services.utils import load_json_file
from plugins.gittxt_api.dependencies import OUTPUT_DIR

router = APIRouter(tags=["Summary"])

@router.get("/{scan_id}")
async def get_summary(scan_id: str = Path(..., description="Scan ID of completed job")):
    try:
        summary_path = OUTPUT_DIR / scan_id / "json"
        return await load_json_file(summary_path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
