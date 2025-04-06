from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from uuid import uuid4
from pathlib import Path
import zipfile
import shutil
from gittxt.core.scanner import scan_repo

router = APIRouter()
UPLOAD_BASE = Path("uploads")

@router.post("/upload")
async def upload_zip(file: UploadFile = File(...)):
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are supported.")

    scan_id = str(uuid4())
    upload_dir = UPLOAD_BASE / scan_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    zip_path = upload_dir / file.filename
    with zip_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(upload_dir)
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid or corrupted zip file.")

    extracted_root = next(upload_dir.iterdir()) if any(upload_dir.iterdir()) else upload_dir

    scan_result = scan_repo(
        repo_path=str(extracted_root),
        output_dir=None,
        subdir=None,
        lite=False,
        non_interactive=True,
        inspect_only=True
    )

    return JSONResponse(content={
        "repo_name": file.filename.replace(".zip", ""),
        "branch": None,
        "tree": scan_result.get("tree", []),
        "textual_files": scan_result.get("textual_files", []),
        "non_textual_files": scan_result.get("non_textual_files", []),
        "summary": scan_result.get("summary", {}),
        "preview_snippets": scan_result.get("preview_snippets", [])
    })
