import shutil
import zipfile
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from gittxt.core.scanner import Scanner
from gittxt.core.output_builder import OutputBuilder
from gittxt_api.api.v1.models.upload_models import UploadResponse
from gittxt_api.api.v1.deps import get_output_dir

async def handle_uploaded_zip(file: UploadFile, lite: bool = False) -> UploadResponse:
    scan_id = str(uuid4())
    output_dir = get_output_dir()
    upload_temp = output_dir / "uploads" / scan_id
    result_dir = output_dir / scan_id

    upload_temp.mkdir(parents=True, exist_ok=True)
    result_dir.mkdir(parents=True, exist_ok=True)

    # Save uploaded zip
    zip_path = upload_temp / file.filename
    with zip_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract repo
    extract_dir = upload_temp / "repo"
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_dir)

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
