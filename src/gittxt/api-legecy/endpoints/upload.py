from fastapi import APIRouter, HTTPException, File, UploadFile, Query
from pathlib import Path
from uuid import uuid4
import shutil
import zipfile
import os

from gittxt.core.logger import Logger
from gittxt.core.config import ConfigManager
from gittxt.core.scanner import Scanner
from gittxt.core.output_builder import OutputBuilder

router = APIRouter()
logger = Logger.get_logger(__name__)
config = ConfigManager.load_config()

OUTPUT_DIR = Path(config.get("output_dir", "./gittxt_output")).resolve()
UPLOAD_DIR = Path(config.get("upload_dir", OUTPUT_DIR / "uploads")).resolve()

@router.post("/upload", tags=["Upload"])
async def upload_zip(
    file: UploadFile = File(...),
    lite: bool = False
):
    """
    Accepts a .zip with user code, extracts, scans, stores results in OUTPUT_DIR/scan_id
    """
    if not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are supported")

    try:
        scan_id = str(uuid4())
        upload_temp = UPLOAD_DIR / scan_id
        output_dir = OUTPUT_DIR / scan_id
        upload_temp.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save the zip
        zip_path = upload_temp / file.filename
        with zip_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract
        extract_dir = upload_temp / "repo"
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(extract_dir)
        repo_name = extract_dir.name

        # minimal scanning
        scanner = Scanner(root_path=extract_dir)
        textual_files, non_textual_files = await scanner.scan_directory()

        # output builder
        mode = "lite" if lite else "rich"
        builder = OutputBuilder(
            repo_name=repo_name,
            output_dir=output_dir,
            output_format="txt,json",  # or add "md" or "zip" if desired
            mode=mode
        )
        await builder.generate_output(
            textual_files, 
            non_textual_files, 
            repo_path=extract_dir,
            create_zip=True
        )

        # optionally remove the extracted repo
        shutil.rmtree(extract_dir, ignore_errors=True)
        zip_path.unlink(missing_ok=True)

        return {
            "scan_id": scan_id,
            "repo_name": repo_name,
            "num_textual_files": len(textual_files),
            "num_non_textual_files": len(non_textual_files),
            "message": "Upload & scan completed",
        }

    except Exception as e:
        logger.error(f"[UPLOAD] Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
