from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse
from pathlib import Path
import json

router = APIRouter()

SUMMARY_FILENAME = "summary.json"
BASE_OUTPUT_DIR = Path("outputs")

@router.get("/summary/{scan_id}")
async def get_summary(scan_id: str = Path(..., description="Scan ID")):
    summary_path = BASE_OUTPUT_DIR / scan_id / SUMMARY_FILENAME

    if not summary_path.exists():
        raise HTTPException(status_code=404, detail="Summary not found.")

    try:
        with summary_path.open("r", encoding="utf-8") as f:
            summary_data = json.load(f)
        return JSONResponse(content=summary_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read summary: {str(e)}")
