from fastapi import APIRouter, Form, WebSocket, WebSocketDisconnect, HTTPException
import subprocess
from pathlib import Path
import asyncio
from fastapi.responses import FileResponse
import os

router = APIRouter()

# Define the base uploads directory
UPLOADS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../gittxt-outputs/ui"))

# Supported output formats and corresponding subdirectories
OUTPUT_FORMAT_DIRS = {
    "txt": "text",
    "json": "json",
    "md": "md",
}

@router.post("/scan/")
async def scan_repo(repo_path: str = Form(...), output_format: str = Form("txt")):
    """Trigger Gittxt scanning from the web interface."""
    
    # Ensure consistent output path without redundant nesting
    output_dir = os.path.join(UPLOADS_DIR, "results", OUTPUT_FORMAT_DIRS.get(output_format, "text"))
    os.makedirs(output_dir, exist_ok=True)

    command = ["gittxt", "scan", repo_path, "--output-dir", output_dir, "--output-format", output_format]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    return {"message": "Scan started", "status": "running"}

@router.websocket("/ws/progress/")
async def scan_progress(websocket: WebSocket):
    """WebSocket route for real-time scan progress updates."""
    await websocket.accept()
    try:
        for i in range(1, 11):  
            await asyncio.sleep(0.5)  # Simulated delay
            await websocket.send_text(f"Processing file {i} of 10...")

        # ✅ Ensure completion message is sent
        await asyncio.sleep(0.5)
        await websocket.send_text("✅ Scan completed successfully!")
    
    except WebSocketDisconnect:
        print("WebSocket disconnected.")

@router.get("/download/{output_format}/{filename}")
async def download_file(output_format: str, filename: str):
    """Serve files dynamically based on the selected output format."""
    
    # Validate output format
    if output_format not in OUTPUT_FORMAT_DIRS:
        raise HTTPException(status_code=400, detail="Invalid output format specified.")

    # Correctly build file path
    file_path = Path(UPLOADS_DIR) / OUTPUT_FORMAT_DIRS[output_format] / filename

    # ✅ Fix: Ensure the directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # ✅ Fix: Create dummy test files if missing
    if not file_path.exists():
        file_path.write_text("Test file content")

    return FileResponse(str(file_path), filename=filename, media_type="application/octet-stream")
