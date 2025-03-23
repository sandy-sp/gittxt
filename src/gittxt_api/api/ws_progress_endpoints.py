from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from gittxt_api.core.scanning_service import SCANS
from gittxt_api.services.artifact_service import available_artifacts
import asyncio
from pathlib import Path

router = APIRouter()

@router.websocket("/ws/{scan_id}")
async def websocket_progress(websocket: WebSocket, scan_id: str):
    await websocket.accept()
    
    # ✅ Check for invalid scan ID immediately
    if scan_id not in SCANS:
        await websocket.close()
        raise WebSocketDisconnect()

    last_progress = -1
    while True:
        scan_data = SCANS.get(scan_id)
        if not scan_data:
            await websocket.send_json({"event": "error", "message": "Scan data missing"})
            break

        status = scan_data["status"]
        current_progress = scan_data.get("progress", 0)

        if current_progress != last_progress:
            await websocket.send_json({"event": "progress", "data": scan_data})
            last_progress = current_progress

        if status in ["done", "error"]:
            payload = {"event": status, "data": scan_data}

            if status == "done":
                repo_name = scan_data.get("repo_name")
                output_dir = Path(scan_data.get("output_dir"))
                payload["artifacts"] = available_artifacts(scan_id, output_dir, repo_name)

            await websocket.send_json(payload)
            break

        await asyncio.sleep(1)

    await websocket.close()
