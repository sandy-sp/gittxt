import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()


@router.get("/download/{scan_id}/{filename}")
async def download(scan_id: str, filename: str):
    temp_base = f"/tmp/scan_{scan_id}_output"  # or use your configured output path
    file_path = os.path.join(temp_base, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")

    return FileResponse(
        file_path,
        filename=filename,
        media_type="application/octet-stream"
    )
