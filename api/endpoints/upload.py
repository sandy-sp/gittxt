from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
from uuid import uuid4
from pathlib import Path
import zipfile
import shutil

from gittxt.core.scanner import scan_repo
from gittxt.core.output_builder import build_outputs

router = APIRouter()

UPLOAD_BASE = Path("uploads")
OUTPUT_BASE = Path("outputs")

@router.post("/upload")
async def upload_zip(request: Request, file: UploadFile = File(...)):
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are supported.")

    scan_id = str(uuid4())
    upload_dir = UPLOAD_BASE / scan_id
    output_dir = OUTPUT_BASE / scan_id

    upload_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    zip_path = upload_dir / file.filename
    with zip_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract ZIP
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(upload_dir)
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid or corrupted zip file.")

    # Try to locate root folder inside zip
    subdirs = [p for p in upload_dir.iterdir() if p.is_dir()]
    repo_root = subdirs[0] if len(subdirs) == 1 else upload_dir

    # Run full scan
    try:
        scan_result = scan_repo(
            repo_path=str(repo_root),
            output_dir=str(output_dir),
            lite=False,
            non_interactive=True
        )

        output_files = build_outputs(
            scan_result=scan_result,
            output_dir=str(output_dir),
            to_txt=True,
            to_md=True,
            to_json=True,
            to_zip=True
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")

    # Build artifact links
    base_url = str(request.base_url).rstrip("/") + f"/download/{scan_id}"
    urls = {
        "txt": f"{base_url}?format=txt" if output_files.get("txt") else None,
        "md": f"{base_url}?format=md" if output_files.get("md") else None,
        "json": f"{base_url}?format=json" if output_files.get("json") else None,
        "zip": f"{base_url}?format=zip" if output_files.get("zip") else None,
    }

    return JSONResponse(content={
        "scan_id": scan_id,
        "repo_name": file.filename.replace(".zip", ""),
        "summary": scan_result.get("summary", {}),
        "download_urls": urls
    })
