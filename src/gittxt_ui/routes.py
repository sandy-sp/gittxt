from fastapi import FastAPI, Form, WebSocket, WebSocketDisconnect, HTTPException
import subprocess
from pathlib import Path
import asyncio
import os
import zipfile
from fastapi.responses import FileResponse

app = FastAPI()

UPLOADS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../gittxt-outputs/ui"))
OUTPUT_FORMAT_DIRS = {"txt": "text", "json": "json", "md": "md"}

@app.post("/scan/")
async def scan_repo(repo_path: str = Form(...), output_format: str = Form("txt"), 
                    include_patterns: str = Form(""), exclude_patterns: str = Form(""), 
                    size_limit: int = Form(None), docs_only: bool = Form(False)):
    """Trigger Gittxt scanning from the web interface."""
    output_dir = os.path.join(UPLOADS_DIR, "results", repo_path.split('/')[-1])
    os.makedirs(output_dir, exist_ok=True)
    
    command = ["gittxt", "scan", repo_path, "--output-dir", output_dir, "--output-format", output_format]
    if include_patterns:
        command.extend(["--include", include_patterns])
    if exclude_patterns:
        command.extend(["--exclude", exclude_patterns])
    if size_limit:
        command.extend(["--size-limit", str(size_limit)])
    if docs_only:
        command.append("--docs-only")
    
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return {"message": "Scan started", "status": "running"}

@app.websocket("/ws/progress/")
async def scan_progress(websocket: WebSocket):
    """WebSocket route for real-time scan progress updates."""
    await websocket.accept()
    try:
        log_file = os.path.join(UPLOADS_DIR, "scan_progress.log")
        while True:
            await asyncio.sleep(0.5)
            if os.path.exists(log_file):
                with open(log_file, "r") as f:
                    progress = f.readlines()
                    for line in progress:
                        await websocket.send_text(line.strip())
    except WebSocketDisconnect:
        print("WebSocket disconnected.")

@app.get("/download/{repo_name}/all")
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
