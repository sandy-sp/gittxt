from fastapi import APIRouter, HTTPException, Path, Query
from fastapi.responses import FileResponse
from pathlib import Path
from api.schemas.download import OutputFormat

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
    if format not in VALID_FORMATS:
        raise HTTPException(status_code=400, detail="Invalid format requested.")

    filename, media_type = VALID_FORMATS[format]
    file_path = BASE_OUTPUT_DIR / scan_id / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Requested file not found.")

    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type=media_type
    )
