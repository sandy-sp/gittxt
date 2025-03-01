from fastapi import FastAPI, Request, Form, UploadFile, File, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path
import shutil
import os
import subprocess
from jinja2 import Template, Environment, FileSystemLoader

app = FastAPI()

# Mount static files (CSS, JS)
app.mount("/static", StaticFiles(directory="web_interface/static"), name="static")

# Set up Jinja2 template engine
templates = Environment(loader=FileSystemLoader("web_interface/templates"))

UPLOAD_DIR = Path("web_interface/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def homepage():
    """Serve the main HTML page."""
    template = templates.get_template("index.html")
    return HTMLResponse(content=template.render(), status_code=200)


@app.post("/scan/")
async def scan_repo(repo_path: str = Form(...), output_format: str = Form("txt")):
    """Trigger Gittxt scanning from the web interface."""
    output_dir = UPLOAD_DIR / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Call the CLI tool
    command = ["gittxt", "scan", repo_path, "--output-dir", str(output_dir), "--output-format", output_format]
    subprocess.run(command, capture_output=True, text=True)

    # List generated files
    files = list(output_dir.glob("*"))
    return {"message": "Scan complete", "files": [str(f) for f in files]}


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """Handle file uploads from the UI."""
    file_path = UPLOAD_DIR / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "message": "File uploaded successfully"}
