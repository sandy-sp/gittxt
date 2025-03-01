from fastapi import APIRouter, Form, WebSocket, WebSocketDisconnect
import subprocess
from pathlib import Path
import asyncio
from fastapi.responses import FileResponse
import os

router = APIRouter()

UPLOAD_DIR = Path("src/gittxt_ui/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/scan/")
async def scan_repo(repo_path: str = Form(...), output_format: str = Form("txt")):
    """Trigger Gittxt scanning from the web interface."""
    output_dir = UPLOAD_DIR / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run the CLI scan command asynchronously
    command = ["gittxt", "scan", repo_path, "--output-dir", str(output_dir), "--output-format", output_format]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    return {"message": "Scan started", "status": "running"}


@router.websocket("/ws/progress/")
async def scan_progress(websocket: WebSocket):
    """WebSocket route for real-time scan progress updates."""
    await websocket.accept()
    try:
        # Fake progress for demonstration (Replace with real CLI scan monitoring)
        for i in range(1, 11):  
            await asyncio.sleep(1)  # Simulate processing delay
            await websocket.send_text(f"Processing file {i} of 10...")
        
        await websocket.send_text("✅ Scan completed successfully!")
    except WebSocketDisconnect:
        print("WebSocket disconnected.")

@router.get("/download/{filename}")
async def download_file(filename: str):
    """Serve scanned output files for download."""
    file_path = UPLOAD_DIR / "results" / filename
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/octet-stream", filename=filename)
    return {"error": "File not found"}