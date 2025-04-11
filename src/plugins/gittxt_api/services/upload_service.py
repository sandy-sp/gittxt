import shutil
import zipfile
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from gittxt.core.scanner import Scanner
from gittxt.core.output_builder import OutputBuilder
from gittxt.api.dependencies import OUTPUT_DIR
from gittxt.api.models.upload_models import UploadResponse

UPLOAD_DIR = OUTPUT_DIR / "uploads"

async def handle_uploaded_zip(file: UploadFile, lite: bool = False) -> UploadResponse:
    scan_id = str(uuid4())
    upload_temp = UPLOAD_DIR / scan_id
    output_dir = OUTPUT_DIR / scan_id

    upload_temp.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    zip_path = upload_temp / file.filename
    with zip_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extract_dir = upload_temp / "repo"
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_dir)

    repo_name = extract_dir.name
    scanner = Scanner(root_path=extract_dir)
    textual_files, non_textual_files = await scanner.scan_directory()

    mode = "lite" if lite else "rich"
    builder = OutputBuilder(
        repo_name=repo_name,
        output_dir=output_dir,
        output_format="txt,json",
        mode=mode
    )
    await builder.generate_output(
        textual_files,
        non_textual_files,
        repo_path=extract_dir,
        create_zip=True
    )

    # Clean temp ZIP and extracted folder
    shutil.rmtree(extract_dir, ignore_errors=True)
    zip_path.unlink(missing_ok=True)

    return UploadResponse(
        scan_id=scan_id,
        repo_name=repo_name,
        num_textual_files=len(textual_files),
        num_non_textual_files=len(non_textual_files),
        message="Upload & scan completed"
    )
