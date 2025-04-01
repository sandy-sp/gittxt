from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from ..models import ScanRequest, ScanResponse
from ..worker import run_scan
from ..storage import get_output_file

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/scan", response_model=ScanResponse)
def scan_repo(request: ScanRequest):
    try:
        return run_scan(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{scan_id}")
def download_file(scan_id: str, format: str):
    file_path = get_output_file(scan_id, format)
    if not file_path:
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=f"{scan_id}.{format}")
