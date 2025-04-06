from fastapi import APIRouter, HTTPException, Path as APIPath  # Renamed Path to avoid clash
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
import logging  # Use standard logging

from gittxt.core.config import ConfigManager  # Updated to use ConfigManager for configuration

router = APIRouter()
logger = logging.getLogger(__name__)  # Standard logger for API layer

@router.delete("/cleanup/{scan_id}", tags=["Cleanup"])
async def cleanup_scan(scan_id: str = APIPath(..., description="Unique identifier for the scan session")):
    """
    Delete temporary files and outputs associated with a scan ID.
    """
    try:
        config = ConfigManager.load_config()
        output_dir_base = Path(config.get("output_dir", "./gittxt_output"))
        target_dir = output_dir_base / scan_id

        if not target_dir.exists() or not target_dir.is_dir():
            raise HTTPException(status_code=404, detail=f"Scan ID '{scan_id}' output directory not found.")

        shutil.rmtree(target_dir)
        logger.info(f"Successfully cleaned up output directory for scan_id: {scan_id}")
        return JSONResponse(content={"detail": f"Scan '{scan_id}' artifacts cleaned up successfully."})

    except HTTPException as http_exc:
        raise http_exc  # Re-raise HTTPExceptions directly
    except Exception as e:
        logger.error(f"Failed to cleanup scan '{scan_id}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error during cleanup: {str(e)}")
