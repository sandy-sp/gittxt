# src/gittxt-ui/backend/api/artifacts_endpoints.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from core.scanning_service import SCANS
from pathlib import Path
import json

router = APIRouter()

@router.get("/{scan_id}/zip")
def download_zip(scan_id: str):
    info = SCANS.get(scan_id)
    if not info or "output_dir" not in info:
        raise HTTPException(404, "Scan not found or no artifacts.")
    zip_path = Path(info["output_dir"]) / "zips" / f"scan_{scan_id}_bundle.zip"
    if not zip_path.exists():
        raise HTTPException(404, "Zip not found.")
    return FileResponse(path=zip_path, filename=f"scan_{scan_id}_bundle.zip")

@router.get("/{scan_id}/json")
def download_json(scan_id: str):
    info = SCANS.get(scan_id)
    if not info or "output_dir" not in info:
        raise HTTPException(404, "Scan not found or no artifacts.")
    json_file = Path(info["output_dir"]) / "json" / f"scan_{scan_id}.json"
    if not json_file.exists():
        raise HTTPException(404, "JSON output not found.")
    data = json.loads(json_file.read_text(encoding="utf-8"))
    return JSONResponse(content=data)
