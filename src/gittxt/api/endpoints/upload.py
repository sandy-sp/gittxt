from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Query, Depends
from fastapi.responses import JSONResponse
from typing import Optional, List
from uuid import uuid4
from pathlib import Path
import zipfile
import shutil

from gittxt.core.scanner import Scanner
from gittxt.core.output_builder import OutputBuilder
from gittxt.utils.tree_utils import generate_tree
from gittxt.api.dependencies.validate_size import validate_zip_size
from gittxt.api.schemas.upload import UploadResponse
from gittxt.__init__ import OUTPUT_DIR  

router = APIRouter()

UPLOAD_BASE = Path("uploads")
OUTPUT_BASE = OUTPUT_DIR  # Use OUTPUT_DIR for output base

@router.post("/upload", response_model=UploadResponse)
async def upload_zip(
    request: Request,
    file: UploadFile = Depends(validate_zip_size),
    lite: bool = Query(False, description="Enable lite mode"),
    include_patterns: Optional[List[str]] = Query(None, description="Glob patterns to include"),
    exclude_patterns: Optional[List[str]] = Query(None, description="Glob patterns to exclude"),
    exclude_dirs: Optional[List[str]] = Query(None, description="Directories to exclude")
):
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are supported.")

    scan_id = str(uuid4())
    upload_dir = UPLOAD_BASE / scan_id
    output_dir = OUTPUT_BASE / scan_id

    # Ensure directories are created before file operations
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

    # Detect repo root (assume top-level folder inside zip)
    extracted_items = list(upload_dir.iterdir())
    repo_root = next((p for p in extracted_items if p.is_dir()), upload_dir)
    repo_name = repo_root.name

    # Run scan
    try:
        scanner = Scanner(
            repo_path=str(repo_root),
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            exclude_dirs=exclude_dirs,
            lite=lite,
            non_interactive=True
        )
        textual_files, non_textual_files = await scanner.scan_directory()

        # Build outputs
        builder = OutputBuilder(
            repo_name=repo_name,
            output_dir=str(output_dir),
            output_format="txt,json,md",
            mode="lite" if lite else "rich",
            scan_results=textual_files,
            scan_id=scan_id,
            repo_path=str(repo_root),
            asset_files=non_textual_files,
        )
        builder.build_outputs()

        # Build directory tree
        tree = generate_tree(repo_root)

        # Auto-clean uploads
        try:
            shutil.rmtree(upload_dir)
        except Exception as e:
            print(f"[WARN] Failed to clean up uploads: {e}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")

    # Build response
    return JSONResponse(content={
        "scan_id": scan_id,
        "repo_name": repo_name,
        "textual_files": [str(f.relative_to(repo_root)) for f in textual_files],
        "non_textual_files": [str(f.relative_to(repo_root)) for f in non_textual_files],
        "tree": tree,
    })
