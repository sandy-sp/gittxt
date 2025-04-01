from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from ..models import ScanRequest, ScanResponse
from ..worker import run_scan
from ..storage import get_output_file, load_summary_data
from src.gittxt_api.main import authenticate, limiter

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/scan", response_model=ScanResponse, dependencies=[Depends(authenticate)])
@limiter.limit("5/minute")  # Limit to 5 requests per minute
def scan_repo(request: ScanRequest):
    try:
        return run_scan(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.get("/download/{scan_id}")
def download_file(scan_id: str, format: str):
    file_path = get_output_file(scan_id, format)
    if not file_path:
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_path, filename=f"{scan_id}.{format}", media_type="application/octet-stream")

@router.get("/scan/{scan_id}", response_class=JSONResponse)
def get_scan_summary(scan_id: str, page: int = 1, page_size: int = 10):
    summary = load_summary_data(scan_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    
    files = summary.get("files", [])
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "scan_id": scan_id,
        "total_files": len(files),
        "page": page,
        "page_size": page_size,
        "files": files[start:end],
    }
