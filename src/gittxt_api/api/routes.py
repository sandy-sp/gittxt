from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from ..models import ScanRequest, ScanResponse
from ..worker import run_scan
from ..storage import get_output_file, load_summary_data

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
    return FileResponse(path=file_path, filename=f"{scan_id}.{format}", media_type="application/octet-stream")

@router.get("/scan/{scan_id}", response_class=JSONResponse)
def get_scan_summary(scan_id: str):
    summary = load_summary_data(scan_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return summary
