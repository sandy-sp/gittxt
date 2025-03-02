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
        # Fake progress for demonstration (Replace with real CLI scan monitoring)
        for i in range(1, 11):  
            await asyncio.sleep(1)  # Simulate processing delay
            await websocket.send_text(f"Processing file {i} of 10...")
        
        await websocket.send_text("✅ Scan completed successfully!")
    except WebSocketDisconnect:
        print("WebSocket disconnected.")

@router.get("/download/{output_format}/{filename}")
async def download_file(output_format: str, filename: str):
    """
    Serve files dynamically based on the selected output format.
    
    Example:
    - /download/txt/output.txt
    - /download/json/output.json
    - /download/md/output.md
    """
    # Ensure the requested format is valid
    if output_format not in OUTPUT_FORMAT_DIRS:
        raise HTTPException(status_code=400, detail="Invalid output format specified.")

    # Build the correct file path based on format
    file_path = os.path.join("src", "gittxt-outputs", "ui", OUTPUT_FORMAT_DIRS[output_format], filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")

    return FileResponse(file_path, filename=filename)
