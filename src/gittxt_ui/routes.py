from fastapi import APIRouter, Form, WebSocket, WebSocketDisconnect, HTTPException
import subprocess
from pathlib import Path
import asyncio
import os
import zipfile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel

router = APIRouter()  # ✅ Use `router` instead of `app`

UPLOADS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../gittxt-outputs/ui"))
OUTPUT_FORMAT_DIRS = {"txt": "text", "json": "json", "md": "md"}

# Load Jinja2 templates
templates = Environment(loader=FileSystemLoader("src/gittxt_ui/templates"))

class ScanRequest(BaseModel):
    repo_path: str
    output_format: str = "txt"
    include_patterns: str = ""
    exclude_patterns: str = ""
    size_limit: int = None
    docs_only: bool = False

@router.get("/")
async def homepage():
    """Serve the main HTML page."""
    template = templates.get_template("index.html")
    return FileResponse(str(template.filename), media_type="text/html")

@router.post("/scan/")
async def scan_repo(scan_data: ScanRequest):
    """Trigger Gittxt scanning from the web interface with real-time tracking."""
    output_dir = os.path.join(UPLOADS_DIR, "results", scan_data.repo_path.split('/')[-1])
    os.makedirs(output_dir, exist_ok=True)
    
    command = ["gittxt", "scan", scan_data.repo_path, "--output-dir", output_dir, "--output-format", scan_data.output_format]
    if scan_data.include_patterns:
        command.extend(["--include", scan_data.include_patterns])
    if scan_data.exclude_patterns:
        command.extend(["--exclude", scan_data.exclude_patterns])
    if scan_data.size_limit:
        command.extend(["--size-limit", str(scan_data.size_limit)])
    if scan_data.docs_only:
        command.append("--docs-only")
    
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return {"message": "Scan started", "status": "running", "pid": process.pid}

@router.websocket("/ws/progress/")
async def scan_progress(websocket: WebSocket):
    """WebSocket route for real-time scan progress updates."""
    await websocket.accept()
    log_file = os.path.join(UPLOADS_DIR, "scan_progress.log")
    try:
        while True:
            await asyncio.sleep(0.5)
            if os.path.exists(log_file):
                with open(log_file, "r") as f:
                    progress = f.readlines()
                    for line in progress:
                        await websocket.send_text(line.strip())
    except WebSocketDisconnect:
        print("WebSocket disconnected.")

@router.get("/scan/status/{pid}")
async def get_scan_status(pid: int):
    """Check the status of the scan process."""
    try:
        os.kill(pid, 0)
        return JSONResponse(content={"status": "running"})
    except OSError:
        return JSONResponse(content={"status": "completed"})

@router.get("/download/{repo_name}/all")
async def download_all(repo_name: str):
    """Compress and serve all scanned output formats for a given repository."""
    repo_output_dir = os.path.join(UPLOADS_DIR, "results", repo_name)
    if not os.path.exists(repo_output_dir):
        raise HTTPException(status_code=404, detail="Repository output not found.")
    
    zip_file_path = os.path.join(UPLOADS_DIR, f"{repo_name}.zip")
    with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(repo_output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, repo_output_dir))
    
    return FileResponse(zip_file_path, filename=f"{repo_name}.zip", media_type="application/zip")
