from fastapi import APIRouter, HTTPException, Query, Path, status
from fastapi.responses import FileResponse
from plugins.gittxt_api.api.v1.deps import get_output_dir

router = APIRouter(tags=["Download"])

@router.get("/{scan_id}", status_code=status.HTTP_200_OK)
async def download_artifact(
    scan_id: str = Path(..., description="Scan ID"),
    format: str = Query(..., pattern="^(txt|json|md|zip)$", description="Download format")
):
    """
    Download a scan artifact in the desired format.
    """
    output_dir = get_output_dir()
    artifact_dir = output_dir / scan_id / format
    if not artifact_dir.exists():
        raise HTTPException(status_code=404, detail=f"No '{format}' folder found.")

    files = list(artifact_dir.glob(f"*.{format}"))
    if not files:
        raise HTTPException(status_code=404, detail=f"No .{format} file found.")

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
