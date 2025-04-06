from fastapi import APIRouter, HTTPException, Path
from pathlib import Path as PathLib
import shutil

from gittxt import OUTPUT_DIR
from gittxt.core.logger import Logger

router = APIRouter()
logger = Logger.get_logger(__name__)

@router.delete("/cleanup/{scan_id}")
async def cleanup_scan(scan_id: str = Path(...)):
    """Delete all files generated for a specific scan"""
    logger.info(f"Cleanup requested for scan {scan_id}")
    
    output_dir = OUTPUT_DIR / scan_id
    
    if not output_dir.exists():
        logger.warning(f"Output directory not found for scan {scan_id}")
        return {"status": "success", "message": f"No data found for scan {scan_id}"}
        
    try:
        # Delete output directory
        shutil.rmtree(output_dir)
        
        # Also check for upload directory
        upload_dir = PathLib("uploads") / scan_id
        if upload_dir.exists():
            shutil.rmtree(upload_dir)
            
        logger.info(f"Successfully deleted data for scan {scan_id}")
        return {"status": "success", "message": f"Deleted all data for scan {scan_id}"}
    except Exception as e:
        logger.error(f"Failed to clean up scan {scan_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete scan data: {str(e)}"
        )
