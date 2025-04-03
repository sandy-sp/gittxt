from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pathlib import Path
import mimetypes

router = APIRouter()

@router.get("/download")
def download_output_file(
    output_dir: str = Query(..., description="Output directory path"),
    file_name: str = Query(..., description="Exact filename to download (e.g., repo.txt, repo.zip)")
):
    # Resolve path safely
    base_path = Path(output_dir).resolve()
    target_file = base_path / file_name

    # Prevent directory traversal
    if not target_file.is_file() or not target_file.resolve().is_relative_to(base_path):
        raise HTTPException(status_code=404, detail=f"File not found or invalid path: {file_name}")

    return FileResponse(
        path=str(target_file),
        filename=target_file.name,
        media_type=_guess_mime_type(target_file)
    )


def _guess_mime_type(file_path: Path) -> str:
    mime, _ = mimetypes.guess_type(file_path.name)
    return mime or "application/octet-stream"
