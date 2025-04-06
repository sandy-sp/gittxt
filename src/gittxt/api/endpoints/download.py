from fastapi import APIRouter, HTTPException, Path, Query
from fastapi.responses import FileResponse
from pathlib import Path
import shutil
from gittxt import OUTPUT_DIR
from gittxt.api.schemas.download import OutputFormat

router = APIRouter()

VALID_FORMATS = {
    OutputFormat.txt: ("gittxt_output.txt", "text/plain"),
    OutputFormat.md: ("gittxt_output.md", "text/markdown"),
    OutputFormat.json: ("gittxt_output.json", "application/json"),
    OutputFormat.zip: ("gittxt_output.zip", "application/zip")
}

BASE_OUTPUT_DIR = Path("outputs")

@router.get("/download/{scan_id}")
async def download_file(
    scan_id: str = Path(..., description="Scan ID"),
    format: OutputFormat = Query(..., description="Output format: txt, md, json, or zip")
):
    filename, media_type = VALID_FORMATS[format]
    file_path = BASE_OUTPUT_DIR / scan_id / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Requested file not found.")

    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type=media_type
    )

@router.get("/download/{scan_id}/artifacts")
async def download_artifacts(scan_id: str = Path(..., description="Scan ID")):
    """
    Return a downloadable ZIP of the scan artifacts.

    Args:
        scan_id (str): Unique identifier for the scan

    Returns:
        FileResponse: ZIP file of the scan outputs
    """
    try:
        artifacts_dir = OUTPUT_DIR / scan_id / "artifacts"
        if not artifacts_dir.exists():
            raise HTTPException(status_code=404, detail="Artifacts not found.")

        zip_path = OUTPUT_DIR / scan_id / f"{scan_id}_artifacts.zip"
        shutil.make_archive(str(zip_path).replace(".zip", ""), 'zip', artifacts_dir)

        return FileResponse(
            path=zip_path,
            filename=zip_path.name,
            media_type='application/zip'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
