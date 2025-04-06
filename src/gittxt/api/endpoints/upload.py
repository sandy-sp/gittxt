from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Query, Depends, Form
from fastapi.responses import JSONResponse
from typing import Optional, List
from uuid import uuid4
from pathlib import Path
import zipfile
import shutil
import os
import traceback

from gittxt.core.scanner import Scanner
from gittxt.core.output_builder import OutputBuilder
from gittxt.utils.tree_utils import generate_tree
from gittxt.api.dependencies.validate_size import validate_file_size
from gittxt.api.schemas.upload import UploadResponse, UploadRequest
from gittxt.__init__ import OUTPUT_DIR
from gittxt.core.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

UPLOAD_BASE = Path("uploads")
OUTPUT_BASE = OUTPUT_DIR

@router.post("/upload", response_model=UploadResponse)
async def upload_zip(
    request: Request,
    file: UploadFile = Depends(validate_file_size),
    lite: bool = Form(False),
    include_patterns: Optional[List[str]] = Query(None, description="Glob patterns to include"),
    exclude_patterns: Optional[List[str]] = Query(None, description="Glob patterns to exclude"),
    exclude_dirs: Optional[List[str]] = Query(None, description="Directories to exclude")
):
    """Upload and scan a ZIP file containing a repository"""
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are supported.")

    # Parse lite flag into UploadRequest schema
    upload_request = UploadRequest(lite=lite)

    scan_id = str(uuid4())
    upload_dir = UPLOAD_BASE / scan_id
    output_dir = OUTPUT_BASE / scan_id
    zip_path = None
    repo_root = None

    try:
        # Ensure directories are created before file operations
        upload_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)

        zip_path = upload_dir / file.filename
        with zip_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract repository from ZIP
        repo_root = upload_dir / "repo"
        repo_root.mkdir(exist_ok=True)
        
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(repo_root)

        # Determine repository name from ZIP structure
        dirs = [d for d in repo_root.iterdir() if d.is_dir()]
        if dirs and len(dirs) == 1:
            # If there's a single top-level directory, use that as repo_root
            repo_root = dirs[0]
        
        repo_name = repo_root.name

        # Initialize scanner and scan files
        scanner = Scanner(
            repo_paths=[str(repo_root)],
            output_dir=str(output_dir),
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            exclude_dirs=exclude_dirs,
            lite_mode=lite
        )

        textual_files, non_textual_files = await scanner.scan_directories()

        # Generate outputs
        builder = OutputBuilder(
            output_formats=["txt", "json"],
            scan_results=textual_files,
            scan_id=scan_id,
            repo_path=str(repo_root),
            asset_files=non_textual_files,
        )
        builder.build_outputs()

        # Build directory tree
        tree = generate_tree(repo_root)

        # Build response
        response = {
            "scan_id": scan_id,
            "repo_name": repo_name,
            "textual_files": [str(f.relative_to(repo_root)) for f in textual_files],
            "non_textual_files": [str(f.relative_to(repo_root)) for f in non_textual_files],
            "tree": tree,
        }
        
        # Auto-clean uploads to save space
        try:
            if zip_path and zip_path.exists():
                os.remove(zip_path)
        except Exception as e:
            logger.warning(f"Failed to clean up zip file: {e}")

        return JSONResponse(content=response)

    except Exception as e:
        logger.error(f"Upload failed: {str(e)}\n{traceback.format_exc()}")
        
        # Clean up any created files/directories on error
        try:
            if zip_path and zip_path.exists():
                os.remove(zip_path)
            if upload_dir.exists():
                shutil.rmtree(upload_dir)
            if output_dir.exists():
                shutil.rmtree(output_dir)
        except Exception as cleanup_error:
            logger.warning(f"Error during cleanup: {cleanup_error}")
            
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")
