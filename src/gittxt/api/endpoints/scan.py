from fastapi import APIRouter, HTTPException, Depends, Query, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional, List
import asyncio
from uuid import uuid4
from pathlib import Path
import traceback
import logging
from gittxt.core.config import ConfigManager
from gittxt.core.repository import RepositoryHandler
from gittxt.core.scanner import Scanner
from gittxt.core.output_builder import OutputBuilder
from gittxt.utils.tree_utils import generate_tree
from gittxt.api.schemas.scan import ScanRequest, ScanResponse, DownloadURLs
from gittxt import OUTPUT_DIR
from gittxt.core.logger import Logger
from gittxt.utils.cleanup_utils import cleanup_temp_folder
from gittxt.api.services.gittxt_runner import run_gittxt_scan, GittxtRunnerError

router = APIRouter()
logger = Logger.get_logger(__name__)

@router.post("/scan", response_model=ScanResponse, tags=["Scan"])
async def scan_repository(scan_request: ScanRequest):
    """
    Scan a GitHub repository
    """
    logger.info(f"Scanning repository: {scan_request.repo_path}")
    
    scan_id = str(uuid4())
    output_dir = OUTPUT_DIR / scan_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Clone repository
        repo_handler = RepositoryHandler(
            repo_url=scan_request.repo_path,
            branch=scan_request.branch
        )
        
        repo_path = await repo_handler.clone_repository()
        logger.debug(f"Cloned repository to {repo_path}")
        
        repo_name = Path(repo_path).name
        
        # Scan repository
        scanner = Scanner(
            repo_paths=[scan_request.repo_path],
            lite=scan_request.lite,
            output_formats=scan_request.output_formats,
            include_patterns=scan_request.include_patterns,
            exclude_patterns=scan_request.exclude_patterns,
            exclude_dirs=scan_request.exclude_dirs,
            branch=scan_request.branch,
            callback_host=scan_request.callback_host,
        )
        
        textual_files, non_textual_files = await scanner.scan_directories()
        logger.info(f"Scan completed: {len(textual_files)} textual files, {len(non_textual_files)} non-textual files")
        
        # Generate outputs
        outputs = scan_request.output_formats or ["txt"]
        builder = OutputBuilder(
            output_formats=outputs,
            repo_name=repo_name,
            output_dir=str(output_dir),
            repo_url=scan_request.repo_url,
            branch=scan_request.branch,
            mode="lite" if scan_request.lite else "rich"
        )
        
        # Build output files
        builder.process_files(textual_files, non_textual_files)
        
        # Generate download URLs
        host = scan_request.callback_host or "http://localhost:8000"
        download_urls = {
            fmt: f"{host}/download/{scan_id}/{fmt}" 
            for fmt in outputs
        }
        download_urls["zip"] = f"{host}/download/{scan_id}/zip"
        
        # Clean up temporary repository
        cleanup_temp_folder(Path(repo_path))
        logger.debug(f"Cleaned up temporary repository: {repo_path}")
        
        response = ScanResponse(
            scan_id=scan_id,
            repo_name=repo_name,
            file_count=len(textual_files) + len(non_textual_files),
            download_urls=download_urls,
            status="completed"
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Repository scan failed: {str(e)}\n{traceback.format_exc()}")
        
        # Clean up on error
        if output_dir.exists():
            import shutil
            shutil.rmtree(output_dir)
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to scan repository: {str(e)}"
        )
