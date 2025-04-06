from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse
from pathlib import Path
import json
from api.schemas.summary import SummaryResponse  # Import the schema

router = APIRouter()

SUMMARY_FILENAME = "summary.json"
BASE_OUTPUT_DIR = Path("outputs")

@router.get("/summary/{scan_id}", response_model=SummaryResponse)
async def get_summary(scan_id: str = Path(..., description="Scan ID")):
    summary_path = BASE_OUTPUT_DIR / scan_id / SUMMARY_FILENAME

    if not summary_path.exists():
        raise HTTPException(status_code=404, detail="Summary not found.")

    try:
        with summary_path.open("r", encoding="utf-8") as f:
            summary_data = json.load(f)

        # Ensure scan_id is included in the response
        summary_data["scan_id"] = scan_id

        # Validate and return the structured response
        try:
            validated_summary = SummaryResponse.parse_obj(summary_data)
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Invalid summary schema: {str(e)}")

        return validated_summary

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format in summary file.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read summary: {str(e)}")
