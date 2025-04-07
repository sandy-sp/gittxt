from fastapi import APIRouter, HTTPException, Path
from pathlib import Path as FilePath
import json
from gittxt import OUTPUT_DIR
from gittxt.api.schemas.summary import SummaryResponse  # Import the schema

router = APIRouter()

@router.get("/summary/{scan_id}", response_model=SummaryResponse)
async def get_summary(scan_id: str = Path(..., description="Scan ID")):
    """
    Return summary and available artifacts for a completed scan.

    Args:
        scan_id (str): ID of the scanned session

    Returns:
        dict: Summary details and artifact paths
    """
    try:
        artifacts_dir = FilePath(OUTPUT_DIR) / scan_id / "artifacts"  # Use FilePath
        if not artifacts_dir.exists():
            raise HTTPException(status_code=404, detail="Scan artifacts not found.")

        # Locate output files
        json_path = artifacts_dir / "gittxt_output.json"  # Use FilePath
        txt_path = artifacts_dir / "gittxt_output.txt"  # Use FilePath
        md_path = artifacts_dir / "gittxt_output.md"  # Use FilePath

        if not json_path.exists():
            raise HTTPException(status_code=404, detail="Output summary missing.")

        # Read summary content from JSON
        with json_path.open("r", encoding="utf-8") as f:
            summary_data = json.load(f)

        repo_name = summary_data.get("repo_name", "unknown")

        return {
            "scan_id": scan_id,
            "repo_name": repo_name,
            "summary": summary_data,
            "artifacts": {
                "json": str(json_path),
                "txt": str(txt_path) if txt_path.exists() else None,
                "md": str(md_path) if md_path.exists() else None,
            },
        }

    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading summary: {e}")
