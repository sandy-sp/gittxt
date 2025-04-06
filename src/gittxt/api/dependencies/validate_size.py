from fastapi import Request, HTTPException
from starlette.datastructures import UploadFile
from typing import Union

MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024

async def validate_file_size(request: Request):
    """
    Validate that uploaded file(s) do not exceed MAX_FILE_SIZE_MB.

    Raises:
        HTTPException: If any file exceeds the max size
    """
    try:
        form = await request.form()
        for item in form.values():
            if isinstance(item, UploadFile):
                # Basic check if file seems valid before reading
                if item.filename and item.size is not None:
                    # Use reported size first for efficiency if available (might be 0 for streams)
                    if item.size > MAX_FILE_SIZE:
                        raise HTTPException(
                            status_code=413,
                            detail=f"Reported file size for '{item.filename}' exceeds limit ({MAX_FILE_SIZE_MB}MB)."
                        )
                    # If size isn't available or 0, read chunks as fallback
                    if item.size == 0:
                        size = 0
                        await item.seek(0)  # Reset pointer just in case
                        async for chunk in item.read(1024 * 1024):  # Read in chunks
                            size += len(chunk)
                            if size > MAX_FILE_SIZE:
                                raise HTTPException(
                                    status_code=413,
                                    detail=f"File '{item.filename}' is too large during streaming. Max allowed is {MAX_FILE_SIZE_MB}MB."
                                )
                        await item.seek(0)  # Reset stream position after reading

    except Exception as e:
        # Catch potential errors during form parsing or file reading
        raise HTTPException(
            status_code=400,  # Bad Request might be more appropriate
            detail=f"Error processing uploaded file: {str(e)}"
        )
