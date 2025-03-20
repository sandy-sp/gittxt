# gittxt-api/api/artifacts_endpoints.py

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
    zip_path = Path(info["output_dir"]) / "zips" / f"{scan_id}_bundle.zip"
    if not zip_path.exists():
        raise HTTPException(404, "Zip not found.")
    return FileResponse(path=zip_path, filename=zip_path.name)

@router.get("/{scan_id}/json")
def download_json(scan_id: str):
    info = SCANS.get(scan_id)
    if not info or "output_dir" not in info:
        raise HTTPException(404, "Scan not found or no artifacts.")
    json_file = Path(info["output_dir"]) / "json" / f"{scan_id}.json"
    if not json_file.exists():
        raise HTTPException(404, "JSON output not found.")
    data = json.loads(json_file.read_text(encoding="utf-8"))
    return JSONResponse(content=data)

@router.get("/{scan_id}/txt")
def download_txt(scan_id: str):
    info = SCANS.get(scan_id)
    if not info or "output_dir" not in info:
        raise HTTPException(404, "Scan not found or no artifacts.")
    txt_file = Path(info["output_dir"]) / "text" / f"{scan_id}.txt"
    if not txt_file.exists():
        raise HTTPException(404, "Text output not found.")
    return FileResponse(path=txt_file, filename=txt_file.name)

@router.get("/{scan_id}/md")
def download_md(scan_id: str):
    info = SCANS.get(scan_id)
    if not info or "output_dir" not in info:
        raise HTTPException(404, "Scan not found or no artifacts.")
    md_file = Path(info["output_dir"]) / "md" / f"{scan_id}.md"
    if not md_file.exists():
        raise HTTPException(404, "Markdown output not found.")
    return FileResponse(path=md_file, filename=md_file.name)
