from fastapi import APIRouter, UploadFile, File, HTTPException
from plugins.gittxt_api.models.upload_models import UploadResponse
from plugins.gittxt_api.services.upload_service import handle_uploaded_zip

router = APIRouter(tags=["Upload"])

@router.post("/", response_model=UploadResponse)
async def upload_zip(file: UploadFile = File(...), lite: bool = False):
    if not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are supported")

    try:
        return await handle_uploaded_zip(file, lite=lite)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
