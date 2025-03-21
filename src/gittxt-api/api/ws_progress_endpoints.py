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
        current_progress = scan_data.get("progress", 0)

        # Send progress updates only on change
        if current_progress != last_progress:
            await websocket.send_json({"event": "progress", "data": scan_data})
            last_progress = current_progress

        if status in ["done", "error"]:
            payload = {"event": status, "data": scan_data}

            if status == "done":
                payload["artifacts"] = {
                    "txt": f"/artifacts/{scan_id}/txt",
                    "json": f"/artifacts/{scan_id}/json",
                    "md": f"/artifacts/{scan_id}/md",
                    "zip": f"/artifacts/{scan_id}/zip",
                }

            await websocket.send_json(payload)
            break

        await asyncio.sleep(1)

    await websocket.close()
