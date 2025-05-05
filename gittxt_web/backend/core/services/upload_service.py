import shutil
import zipfile
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile, HTTPException

from gittxt.core.scanner import Scanner
from gittxt.core.output_builder import OutputBuilder
from gittxt_web.api.v1.models.upload_models import UploadResponse
from gittxt_web.api.v1.deps import get_output_dir

async def handle_uploaded_zip(file: UploadFile, lite: bool = False) -> UploadResponse:
    # Validate file type
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only ZIP files are allowed.")

    # Validate file size (e.g., max 10 MB)
    file_size = await file.read()
    if len(file_size) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 10 MB limit.")

    # Reset file pointer after reading
    await file.seek(0)

    scan_id = str(uuid4())
    output_dir = get_output_dir()
    upload_temp = output_dir / "uploads" / scan_id
    result_dir = output_dir / scan_id

    upload_temp.mkdir(parents=True, exist_ok=True)
    result_dir.mkdir(parents=True, exist_ok=True)

    # Save uploaded zip
    zip_path = upload_temp / file.filename
    with open(zip_path, "wb") as f:
        f.write(file_size)

    # Extract repo
    extract_dir = upload_temp / "repo"
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    # Scan and classify
    repo_name = extract_dir.name
    scanner = Scanner(root_path=extract_dir)
    textual_files, non_textual_files = await scanner.scan_directory()

    # Generate outputs
    mode = "lite" if lite else "rich"
    builder = OutputBuilder(
        repo_name=repo_name,
        output_dir=result_dir,
        output_format="txt,json",
        mode=mode
    )
    await builder.generate_output(
        textual_files,
        non_textual_files,
        repo_path=extract_dir,
        create_zip=True
    )

    # Cleanup
    shutil.rmtree(extract_dir, ignore_errors=True)
    zip_path.unlink(missing_ok=True)

    return UploadResponse(
        scan_id=scan_id,
        repo_name=repo_name,
        num_textual_files=len(textual_files),
        num_non_textual_files=len(non_textual_files),
        message="Upload & scan completed"
    )
