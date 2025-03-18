# src/gittxt-ui/backend/api/ws_progress_endpoints.py

from fastapi import APIRouter, WebSocket, HTTPException
from core.scanning_service import SCANS
import asyncio

router = APIRouter()

@router.websocket("/ws/{scan_id}")
async def websocket_progress(websocket: WebSocket, scan_id: str):
    await websocket.accept()
    if scan_id not in SCANS:
        await websocket.send_json({"event": "error", "message": "Scan not found"})
        await websocket.close()
        return

    last_progress = -1
    while True:
        scan_data = SCANS.get(scan_id)
        if not scan_data:
            await websocket.send_json({"event": "error", "message": "Scan data missing"})
            break

        status = scan_data["status"]
        current_progress = scan_data["progress"]

        # Send progress
        if current_progress != last_progress:
            await websocket.send_json({"event": "progress", "data": scan_data})
            last_progress = current_progress

        if status in ["done", "error"]:
            # Send final data
            await websocket.send_json({"event": status, "data": scan_data})
            break

        await asyncio.sleep(1)

    await websocket.close()
