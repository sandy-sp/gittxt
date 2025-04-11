from fastapi import APIRouter, HTTPException, Query, Path
from fastapi.responses import FileResponse
from fastapi import Path
from plugins.gittxt_api.dependencies import OUTPUT_DIR

router = APIRouter(tags=["Download"])

@router.get("/{scan_id}")
async def download_artifact(
    scan_id: str = Path(..., description="Scan ID of completed job"),
    format: str = Query(..., pattern="^(txt|json|md|zip)$", description="Artifact format to download")
):
    scan_path = OUTPUT_DIR / scan_id
    if not scan_path.exists():
        raise HTTPException(status_code=404, detail="Scan ID not found")

    artifact_dir = scan_path / format
    if not artifact_dir.exists():
        raise HTTPException(status_code=404, detail=f"No '{format}' folder found for scan")

    files = list(artifact_dir.glob(f"*.{format}"))
    if not files:
        raise HTTPException(status_code=404, detail=f"No .{format} files found in artifact folder")

    file_path = files[0]
    media_map = {
        "txt": "text/plain",
        "json": "application/json",
        "md": "text/markdown",
        "zip": "application/zip"
    }

    return FileResponse(
        path=str(file_path),
        media_type=media_map.get(format, "application/octet-stream"),
        filename=file_path.name
    )
