from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pathlib import Path
import mimetypes

router = APIRouter()

@router.get("/download")
def download_output_file(
    output_dir: str = Query(..., description="Output directory path"),
    file_name: str = Query(..., description="Exact filename to download")
):
    base_path = Path(output_dir).resolve()
    target_file = find_file_recursive(base_path, file_name)

    if not target_file or not target_file.is_file():
        raise HTTPException(status_code=404, detail=f"File not found: {file_name}")

    return FileResponse(
        path=str(target_file),
        filename=target_file.name,
        media_type=_guess_mime_type(target_file)
    )

def find_file_recursive(output_dir: Path, file_name: str):
    for path in output_dir.rglob("*"):
        if path.name == file_name and path.is_file():
            return path
    return None

def _guess_mime_type(file_path: Path) -> str:
    mime, _ = mimetypes.guess_type(file_path.name)
    return mime or "application/octet-stream"
