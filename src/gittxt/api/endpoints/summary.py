from fastapi import APIRouter, HTTPException, Path
from pathlib import Path as PathLib

from gittxt import OUTPUT_DIR
from gittxt.core.logger import Logger
from gittxt.utils.summary_utils import generate_summary

router = APIRouter()
logger = Logger.get_logger(__name__)

@router.get("/summary/{scan_id}")
async def get_scan_summary(scan_id: str = Path(...)):
    """Get summary information for a scan"""
    logger.info(f"Summary requested for scan {scan_id}")
    
    output_dir = OUTPUT_DIR / scan_id
    
    if not output_dir.exists():
        logger.warning(f"Output directory not found for scan {scan_id}")
        raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found")
        
    try:
        # Find all files in the output directory
        all_files = []
        for root, _, files in PathLib(output_dir).walk():
            for file in files:
                if file.endswith(('.txt', '.json', '.md')):
                    all_files.append(PathLib(root) / file)
        
        if not all_files:
            raise HTTPException(status_code=404, detail="No files found for this scan")
            
        # Generate and return summary
        summary = await generate_summary(all_files)
        return summary
        
    except Exception as e:
        logger.error(f"Failed to generate summary for scan {scan_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate summary: {str(e)}"
        )
