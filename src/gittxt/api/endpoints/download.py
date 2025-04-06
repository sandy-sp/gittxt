from fastapi import APIRouter, HTTPException, Path, Query
from fastapi.responses import FileResponse
from pathlib import Path as FilePath
import shutil

from gittxt import OUTPUT_DIR
from gittxt.api.schemas.download import OutputFormat

router = APIRouter()

VALID_FORMATS = {
    OutputFormat.txt: ("artifacts/gittxt_output.txt", "text/plain"),
    OutputFormat.md: ("artifacts/gittxt_output.md", "text/markdown"),
    OutputFormat.json: ("artifacts/gittxt_output.json", "application/json"),
    OutputFormat.zip: ("artifacts.zip", "application/zip"),
}


@router.get("/download/{scan_id}")
async def download_file(
    scan_id: str = Path(..., description="Scan ID"),
    format: OutputFormat = Query(..., description="Output format: txt, md, json, or zip")
):
    """
    Download a specific output format for the scan result.

    Args:
        scan_id (str): Unique scan session ID
        format (OutputFormat): Desired file format

    Returns:
        FileResponse: Streamed file response
    """
    filename, media_type = VALID_FORMATS[format]
    scan_path = FilePath(OUTPUT_DIR) / scan_id

    # Handle ZIP bundling logic
    if format == OutputFormat.zip:
        artifacts_dir = scan_path / "artifacts"
        zip_path = scan_path / filename

        if not zip_path.exists():
            if not artifacts_dir.exists():
                raise HTTPException(status_code=404, detail="Artifacts directory not found.")
            shutil.make_archive(str(zip_path).replace(".zip", ""), 'zip', artifacts_dir)

        return FileResponse(
            path=zip_path,
            filename=zip_path.name,
            media_type=media_type,
        )

    # Handle individual output formats (txt, md, json)
    file_path = scan_path / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Requested file '{filename}' not found.")

    return FileResponse(
        path=file_path,
        filename=FilePath(filename).name,
        media_type=media_type,
    )


@router.get("/download/{scan_id}/artifacts")
async def download_artifacts(scan_id: str = Path(..., description="Scan ID")):
    """
    Download a ZIP of the full artifacts directory (legacy version of zip).

    Args:
        scan_id (str): Unique identifier for the scan

    Returns:
        FileResponse: ZIP file of the scan outputs
    """
    try:
        scan_path = FilePath(OUTPUT_DIR) / scan_id
        artifacts_dir = scan_path / "artifacts"
        zip_path = scan_path / f"{scan_id}_artifacts.zip"

        if not artifacts_dir.exists():
            raise HTTPException(status_code=404, detail="Artifacts directory not found.")

        if not zip_path.exists():
            shutil.make_archive(str(zip_path).replace(".zip", ""), 'zip', artifacts_dir)

        return FileResponse(
            path=zip_path,
            filename=zip_path.name,
            media_type="application/zip"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
