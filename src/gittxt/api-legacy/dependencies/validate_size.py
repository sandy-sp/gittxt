from fastapi import Request, HTTPException, UploadFile
from starlette.datastructures import UploadFile as StarletteUploadFile
from typing import Union
from gittxt.core.logger import Logger
from gittxt.core.config import ConfigManager

logger = Logger.get_logger(__name__)
config = ConfigManager.load_config()

# Default to 50MB if not specified
MAX_UPLOAD_SIZE = config.get("max_upload_size", 52428800)

async def validate_file_size(file: UploadFile) -> UploadFile:
    """Validate that the uploaded file doesn't exceed max size"""
    # Read and immediately seek to beginning
    file_size = 0
    chunk_size = 1024 * 1024  # 1MB chunks
    
    # Read in chunks to avoid loading entire file into memory
    chunk = await file.read(chunk_size)
    while chunk:
        file_size += len(chunk)
        if file_size > MAX_UPLOAD_SIZE:
            logger.warning(f"Upload rejected: file size {file_size} exceeds limit {MAX_UPLOAD_SIZE}")
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds the limit of {MAX_UPLOAD_SIZE/1024/1024:.1f}MB"
            )
        chunk = await file.read(chunk_size)
    
    # Reset file to beginning
    await file.seek(0)
    logger.debug(f"File size validation passed: {file_size} bytes")
    return file
