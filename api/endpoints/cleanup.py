from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil

router = APIRouter()

BASE_OUTPUT_DIR = Path("outputs")

@router.delete("/cleanup/{scan_id}")
async def cleanup_scan(scan_id: str = Path(..., description="Scan ID")):
    target_dir = BASE_OUTPUT_DIR / scan_id

    if not target_dir.exists():
        raise HTTPException(status_code=404, detail="Scan ID not found.")

    try:
        shutil.rmtree(target_dir)
        return JSONResponse(content={"detail": f"Scan {scan_id} cleaned up."})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup scan: {str(e)}")
