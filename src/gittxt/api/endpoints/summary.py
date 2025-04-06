from fastapi import APIRouter, HTTPException, Path
from pathlib import Path as FilePath  # Alias pathlib.Path
import json
from gittxt import OUTPUT_DIR
from gittxt.api.schemas.summary import SummaryResponse  # Import the schema
from gittxt.api.services.gittxt_runner import get_gittxt_summary, GittxtRunnerError
from gittxt.core.logger import Logger
router = APIRouter()

@router.get("/summary/{scan_id}", response_model=SummaryResponse, tags=["Summary"])
async def retrieve_summary(scan_id: str = Path(..., description="Unique identifier for the scan session")):
    """
    Retrieve the summary data for a completed Gittxt scan.
    Returns 404 if scan ID not found, 202 if still processing, 409 if failed.
    """
    logger.info(f"Received request for summary of scan_id: {scan_id}")
    try:
        summary_data = await get_gittxt_summary(scan_id)
        return summary_data
    except GittxtRunnerError as runner_exc:
        # Specific status codes are handled by the runner function exception
        logger.warning(f"Summary retrieval issue for {scan_id}: {runner_exc.message} (Status: {runner_exc.status_code})")
        raise HTTPException(status_code=runner_exc.status_code, detail=runner_exc.message)
    except Exception as e:
        logger.error(f"Unexpected error retrieving summary for {scan_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error retrieving summary: {str(e)}")
