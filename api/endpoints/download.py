from fastapi import APIRouter, HTTPException, Path, Query
from fastapi.responses import FileResponse
from pathlib import Path

router = APIRouter()

VALID_FORMATS = {
    "txt": "gittxt_output.txt",
    "md": "gittxt_output.md",
    "json": "gittxt_output.json",
    "zip": "gittxt_output.zip"
}

BASE_OUTPUT_DIR = Path("outputs")

@router.get("/download/{scan_id}")
async def download_file(
    scan_id: str = Path(..., description="Scan ID"),
    format: str = Query(..., description="Output format: txt, md, json, or zip")
):
    if format not in VALID_FORMATS:
        raise HTTPException(status_code=400, detail="Invalid format requested.")

    file_path = BASE_OUTPUT_DIR / scan_id / VALID_FORMATS[format]

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Requested file not found.")

    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type="application/octet-stream"
    )
