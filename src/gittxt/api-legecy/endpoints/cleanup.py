from fastapi import APIRouter, HTTPException, Path
from pathlib import Path as FilePath  # Rename the import to avoid conflict
import shutil

from gittxt.core.logger import Logger
from gittxt.core.config import ConfigManager

router = APIRouter()
logger = Logger.get_logger(__name__)
config = ConfigManager.load_config()

OUTPUT_DIR = FilePath(config.get("output_dir", "./gittxt_output")).resolve()

@router.delete("/cleanup/{scan_id}", tags=["Cleanup"])
async def cleanup_scan(scan_id: str = Path(...)):
    """
    Remove all artifacts in OUTPUT_DIR/<scan_id>
    """
    scan_path = OUTPUT_DIR / scan_id
    if not scan_path.exists():
        raise HTTPException(status_code=404, detail="Scan ID not found")

    shutil.rmtree(scan_path, ignore_errors=True)
    return {"status": "ok", "message": f"Deleted {scan_id} from server"}
