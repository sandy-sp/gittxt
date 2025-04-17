from fastapi import APIRouter, UploadFile, File, HTTPException, status
from gittxt_api.api.v1.models.upload_models import UploadResponse
from gittxt_api.core.services.upload_service import handle_uploaded_zip
from gittxt_api.api.v1.models.response_models import ApiResponse

router = APIRouter(tags=["Upload"])

@router.post("/", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_zip(file: UploadFile = File(...), lite: bool = False):
    """
    Accepts a zipped repository, scans and processes files.
    """
    if not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are supported")

    try:
        upload_result = await handle_uploaded_zip(file, lite=lite)
        return ApiResponse(message="Upload & scan completed", data=upload_result.dict())

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
