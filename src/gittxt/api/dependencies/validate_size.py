from fastapi import UploadFile, HTTPException
from starlette.requests import Request

MAX_ZIP_SIZE_MB = 50  # dynamic option if needed

async def validate_zip_size(file: UploadFile, request: Request):
    contents = await file.read()
    file_size_mb = len(contents) / (1024 * 1024)

    if file_size_mb > MAX_ZIP_SIZE_MB:
        raise HTTPException(
            status_code=413,
            detail=f"ZIP file exceeds max allowed size of {MAX_ZIP_SIZE_MB} MB"
        )

    file.file.seek(0)  # reset pointer
    return file
