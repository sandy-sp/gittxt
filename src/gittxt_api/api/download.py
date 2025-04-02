from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

router = APIRouter()

@router.get("/zip")
def download_zip(output_dir: str):
    if not os.path.exists(output_dir):
        raise HTTPException(status_code=404, detail="Output directory not found.")

    # Look for a .zip file in the output directory
    zip_files = [f for f in os.listdir(output_dir) if f.endswith(".zip")]

    if not zip_files:
        raise HTTPException(status_code=404, detail="No ZIP file found in output directory.")

    zip_path = os.path.join(output_dir, zip_files[0])

    return FileResponse(
        zip_path,
        filename=zip_files[0],
        media_type="application/zip"
    )
