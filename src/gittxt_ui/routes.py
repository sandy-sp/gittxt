from fastapi import APIRouter, Form
import subprocess
from pathlib import Path

router = APIRouter()

UPLOAD_DIR = Path("src/gittxt_ui/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/scan/")
async def scan_repo(repo_path: str = Form(...), output_format: str = Form("txt")):
    """Trigger Gittxt scanning from the web interface."""
    output_dir = UPLOAD_DIR / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Call CLI tool
    command = ["gittxt", "scan", repo_path, "--output-dir", str(output_dir), "--output-format", output_format]
    subprocess.run(command, capture_output=True, text=True)

    # List generated files
    files = list(output_dir.glob("*"))
    return {"message": "Scan complete", "files": [str(f) for f in files]}
