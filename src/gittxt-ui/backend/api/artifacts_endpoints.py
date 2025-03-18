# src/gittxt-ui/backend/api/artifacts_endpoints.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from core.scanning_service import SCANS
from pathlib import Path
import json

router = APIRouter()

@router.get("/{scan_id}/zip")
def download_zip(scan_id: str):
    """
    Download the .zip artifact created by Gittxt OutputBuilder for the given scan_id.
    We keep ephemeral data until user calls the /scans/{scan_id}/close endpoint.
    """
    info = SCANS.get(scan_id)
    if not info or "output_dir" not in info:
        raise HTTPException(404, "Scan not found or no artifacts.")
    zip_path = Path(info["output_dir"]) / "zips" / f"scan_{scan_id}_bundle.zip"
    if not zip_path.exists():
        raise HTTPException(404, "Zip not found.")
    return FileResponse(path=zip_path, filename=f"scan_{scan_id}_bundle.zip")

@router.get("/{scan_id}/json")
def download_json(scan_id: str):
    """
    Download the JSON summary from the Gittxt OutputBuilder for the given scan_id.
    Again, ephemeral data remains until /scans/{scan_id}/close is called.
    """
    info = SCANS.get(scan_id)
    if not info or "output_dir" not in info:
        raise HTTPException(404, "Scan not found or no artifacts.")
    json_file = Path(info["output_dir"]) / "json" / f"scan_{scan_id}.json"
    if not json_file.exists():
        raise HTTPException(404, "JSON output not found.")
    data = json.loads(json_file.read_text(encoding="utf-8"))
    return JSONResponse(content=data)

@router.get("/{scan_id}/txt")
def download_txt(scan_id: str):
    """
    Download the .txt artifact from Gittxt's OutputBuilder text output folder.
    """
    info = SCANS.get(scan_id)
    if not info or "output_dir" not in info:
        raise HTTPException(404, "Scan not found or no artifacts.")
    txt_file = Path(info["output_dir"]) / "text" / f"scan_{scan_id}.txt"
    if not txt_file.exists():
        raise HTTPException(404, "Text output not found.")
    return FileResponse(path=str(txt_file), filename=f"scan_{scan_id}.txt")

@router.get("/{scan_id}/md")
def download_md(scan_id: str):
    """
    Download the .md artifact from Gittxt's OutputBuilder markdown output folder.
    """
    info = SCANS.get(scan_id)
    if not info or "output_dir" not in info:
        raise HTTPException(404, "Scan not found or no artifacts.")
    md_file = Path(info["output_dir"]) / "md" / f"scan_{scan_id}.md"
    if not md_file.exists():
        raise HTTPException(404, "Markdown output not found.")
    return FileResponse(path=str(md_file), filename=f"scan_{scan_id}.md")
