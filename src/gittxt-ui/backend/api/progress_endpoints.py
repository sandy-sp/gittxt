# src/gittxt-ui/backend/api/progress_endpoints.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from core.scanning_service import SCANS
import asyncio

router = APIRouter()

@router.get("/sse/{scan_id}")
async def sse_progress(scan_id: str):
    """
    Server-Sent Events endpoint for real-time progress updates.
    The frontend can connect with an EventSource:
        new EventSource("/progress/sse/" + scan_id);
    """

    if scan_id not in SCANS:
        raise HTTPException(status_code=404, detail="Scan not found")

    async def event_generator():
        last_progress = -1
        while True:
            scan_data = SCANS.get(scan_id)
            if not scan_data:
                # If somehow it's missing
                yield "event: error\ndata: {\"msg\": \"Scan ID disappeared\"}\n\n"
                break

            status = scan_data["status"]
            if status in ["done", "error"]:
                # Once the scan is finished or error, send final data and exit
                yield f"event: done\ndata: {scan_data}\n\n"
                break

            current_progress = scan_data["progress"]
            if current_progress != last_progress:
                # Only send update if progress changed or every few seconds
                yield f"event: progress\ndata: {scan_data}\n\n"
                last_progress = current_progress

            await asyncio.sleep(1)  # poll interval

    return StreamingResponse(event_generator(), media_type="text/event-stream")
