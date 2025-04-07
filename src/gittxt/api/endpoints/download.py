from fastapi import APIRouter, HTTPException, Query, Path
from fastapi.responses import FileResponse
from pathlib import Path

from gittxt.core.logger import Logger
from gittxt.core.config import ConfigManager

router = APIRouter()
logger = Logger.get_logger(__name__)
config = ConfigManager.load_config()

OUTPUT_DIR = Path(config.get("output_dir", "./gittxt_output")).resolve()

@router.get("/download/{scan_id}", tags=["Download"])
async def download_artifact(
    scan_id: str,
    format: str = Query(..., pattern="^(txt|json|md|zip)$")
):
    """
    Return the first .txt, .json, .md, or .zip from OUTPUT_DIR/<scan_id>/subfolder
    """
    scan_path = OUTPUT_DIR / scan_id
    if not scan_path.exists():
        raise HTTPException(status_code=404, detail="Scan ID not found")

    artifact_dir = scan_path / format
    if not artifact_dir.exists():
        raise HTTPException(status_code=404, detail=f"No {format} subfolder found")

    files = list(artifact_dir.glob(f"*.{format}"))
    if not files:
        raise HTTPException(status_code=404, detail=f"No .{format} files found")

    file_path = files[0]
    media_map = {
        "txt": "text/plain",
        "json": "application/json",
        "md": "text/markdown",
        "zip": "application/zip",
    }
    return FileResponse(
        path=str(file_path),
        media_type=media_map.get(format, "application/octet-stream"),
        filename=file_path.name
    )
