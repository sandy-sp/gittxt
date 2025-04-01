from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

router = APIRouter()

@router.get("/zip")
def download_zip(output_dir: str):
    zip_path = os.path.join(output_dir, "bundle.zip")

    if not os.path.isfile(zip_path):
        raise HTTPException(status_code=404, detail="ZIP file not found.")

    return FileResponse(zip_path, filename="gittxt_output.zip", media_type="application/zip")
