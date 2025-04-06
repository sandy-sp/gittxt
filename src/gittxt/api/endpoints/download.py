from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import FileResponse, Response
import os
from pathlib import Path as PathLib
import zipfile
import tempfile
import shutil

from gittxt import OUTPUT_DIR
from gittxt.core.constants import TEXT_DIR, JSON_DIR, MD_DIR
from gittxt.core.logger import Logger

router = APIRouter()
logger = Logger.get_logger(__name__)

@router.get("/download/{scan_id}/{format}")
async def download_scan_output(scan_id: str = Path(...), format: str = Path(...)):
    """
    Download scan output in the specified format
    
    - format: txt, json, md, zip
    """
    logger.info(f"Download requested for scan {scan_id}, format: {format}")
    
    output_base = OUTPUT_DIR / scan_id
    
    if not output_base.exists():
        logger.warning(f"Output directory not found for scan {scan_id}")
        raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found")
    
    # Map format to directory and file extension
    format_mapping = {
        "txt": (TEXT_DIR, "txt"),
        "json": (JSON_DIR, "json"),
        "md": (MD_DIR, "md"),
    }
    
    if format in format_mapping:
        dir_name, ext = format_mapping[format]
        output_dir = output_base / dir_name
        
        # Find the first file with the right extension
        try:
            output_file = next(output_dir.glob(f"*.{ext}"))
            logger.debug(f"Serving file: {output_file}")
            return FileResponse(
                path=output_file,
                media_type=f"application/{ext}",
                filename=f"{scan_id}.{ext}"
            )
        except (StopIteration, FileNotFoundError):
            logger.warning(f"No {format} file found in {output_dir}")
            raise HTTPException(status_code=404, detail=f"No {format} output found")
            
    elif format == "zip":
        # Create ZIP archive of all output files
        try:
            temp_dir = tempfile.mkdtemp()
            zip_path = PathLib(temp_dir) / f"{scan_id}.zip"
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(output_base):
                    rel_dir = os.path.relpath(root, output_base)
                    for file in files:
                        if file.endswith((".txt", ".json", ".md")):
                            zipf.write(
                                os.path.join(root, file),
                                arcname=os.path.join(rel_dir, file)
                            )
            
            logger.debug(f"Created ZIP archive at {zip_path}")
            
            def cleanup():
                """Remove temp dir after response is sent"""
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    logger.error(f"Failed to clean up temp dir: {e}")
            
            return FileResponse(
                path=zip_path,
                media_type="application/zip",
                filename=f"{scan_id}.zip",
                background=cleanup
            )
        except Exception as e:
            logger.error(f"Failed to create ZIP: {e}")
            raise HTTPException(status_code=500, detail="Failed to create ZIP archive")
    else:
        logger.warning(f"Invalid format requested: {format}")
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid format. Supported formats: txt, json, md, zip"
        )
