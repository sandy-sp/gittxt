from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Query, Depends, Form
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict
from uuid import uuid4
from pathlib import Path
import zipfile
import shutil
import os
import traceback
import asyncio

from gittxt.core.scanner import Scanner
from gittxt.core.output_builder import OutputBuilder
from gittxt.utils.tree_utils import generate_tree
from gittxt.api.dependencies.validate_size import validate_file_size
from gittxt.api.schemas.upload import UploadResponse, UploadRequest
from gittxt import OUTPUT_DIR
from gittxt.core.logger import Logger
from gittxt.core.config import ConfigManager

# Load the config
config = ConfigManager.load_config()

# Define unified paths
UPLOAD_DIR = Path(config.get("upload_dir", OUTPUT_DIR / "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)  # Ensure directory exists

router = APIRouter()
logger = Logger.get_logger(__name__)

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
    logger.info(f"Processing upload: {file.filename}, lite mode: {lite}")
    
    if not file.filename.endswith(".zip"):
        logger.warning(f"Invalid file upload attempt: {file.filename}")
        raise HTTPException(status_code=400, detail="Only .zip files are supported")

    # Parse lite flag into UploadRequest schema
    lite = lite if isinstance(lite, bool) else lite.lower() == "true"
    upload_request = UploadRequest(lite=lite)

    scan_id = str(uuid4())
    upload_dir = UPLOAD_DIR / scan_id
    output_dir = OUTPUT_BASE / scan_id
    zip_path = None
    repo_root = None

    try:
        # Ensure directories are created
        upload_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Created directories for scan {scan_id}")

        zip_path = upload_dir / file.filename
        with zip_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.debug(f"Saved uploaded file to {zip_path}")

        # Extract repository from ZIP
        repo_root = upload_dir / "repo"
        repo_root.mkdir(exist_ok=True)
        
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(repo_root)
            logger.debug(f"Extracted ZIP to {repo_root}")

        # Determine repository name from ZIP structure
        dirs = [d for d in repo_root.iterdir() if d.is_dir()]
        if dirs and len(dirs) == 1:
            # If there's a single top-level directory, use that as repo_root
            repo_root = dirs[0]
        
        repo_name = repo_root.name
        logger.info(f"Processing repository: {repo_name}")

        # Initialize scanner and scan files
        scanner = Scanner(
            root_path=str(repo_root),
            mode="lite" if lite else "rich",  # Updated to use mode instead of lite_mode
            output_formats=["txt", "json"],
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            exclude_dirs=exclude_dirs,
            branch=None,  # Branch is not applicable for uploads
            callback_host=None,  # Callback host is not applicable for uploads
        )

        # Call scan_directory (not scan_directories)
        textual_files, non_textual_files = await scanner.scan_directory()
        logger.info(f"Scan completed: {len(textual_files)} textual files, {len(non_textual_files)} non-textual files")

        # Generate outputs
        outputs = ["txt", "json"]
        builder = OutputBuilder(
            output_formats=outputs,
            repo_name=repo_name,
            output_dir=str(output_dir),  # Ensure correct output_dir is passed
            mode="lite" if lite else "rich",  # Ensure mode is consistent with CLI
        )
        
        # Build output files
        builder.process_files(textual_files, non_textual_files)
        logger.debug(f"Generated output formats: {outputs}")

        # Generate file tree as a nested dict
        tree, *_ = generate_tree(repo_root, count_items=True)
        logger.debug(f"Generated file tree for {repo_name}")

        # Write a status log file
        status_log_path = output_dir / "status.log"
        status_log_path.write_text("Scan completed successfully.")
        logger.debug(f"Wrote status log to {status_log_path}")

        # Build download URLs
        base_url = f"{request.url.scheme}://{request.url.netloc}"
        download_urls = {
            fmt: f"{base_url}/download/{scan_id}/{fmt}" for fmt in outputs
        }
        download_urls["zip"] = f"{base_url}/download/{scan_id}/zip"
        
        # Build summary data
        summary = {
            "total_files": len(textual_files) + len(non_textual_files),
            "textual_files": len(textual_files),
            "non_textual_files": len(non_textual_files),
        }

        # Build response
        response = {
            "scan_id": scan_id,
            "repo_name": repo_name,
            "summary": summary,
            "download_urls": download_urls,
            "tree": tree,
        }

        # Cleanup extracted repository folder
        if repo_root.exists():
            shutil.rmtree(repo_root)
            logger.debug(f"Cleaned up extracted repository folder: {repo_root}")

        # Auto-clean uploads to save space (keep extracted files for download)
        if zip_path and zip_path.exists():
            os.remove(zip_path)
            logger.debug(f"Cleaned up ZIP file: {zip_path}")

        logger.debug(f"Returning response for scan {scan_id}")
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
            logger.debug(f"Cleaned up resources after error for scan {scan_id}")
        except Exception as cleanup_error:
            logger.warning(f"Error during cleanup: {cleanup_error}")
            
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")
