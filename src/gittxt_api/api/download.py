from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pathlib import Path

router = APIRouter()

@router.get("/download")
def download_output_file(
    output_dir: str = Query(..., description="Full output directory path"),
    file_name: str = Query(..., description="Name of the file to download")
):
    full_path = Path(output_dir) / file_name
    if not full_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {file_name}")

    return FileResponse(
        path=str(full_path),
        filename=file_name,
        media_type=_guess_mime(file_name)
    )

def _guess_mime(filename: str) -> str:
    if filename.endswith(".zip"):
        return "application/zip"
    elif filename.endswith(".json"):
        return "application/json"
    elif filename.endswith(".md"):
        return "text/markdown"
    elif filename.endswith(".txt"):
        return "text/plain"
    return "application/octet-stream"
