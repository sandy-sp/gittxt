from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from core.scanning_service import SCANS
from pathlib import Path
import json
from services.artifact_service import resolve_artifact_paths, available_artifacts

router = APIRouter()

@router.get("/{scan_id}/{artifact}")
def download_artifact(scan_id: str, artifact: str):
    info = SCANS.get(scan_id)
    if not info or "output_dir" not in info:
        raise HTTPException(404, "Scan not found or incomplete.")

    repo_name = info.get("repo_name")
    output_dir = Path(info["output_dir"])

    artifact_paths = resolve_artifact_paths(scan_id, output_dir, repo_name)

    if artifact not in artifact_paths:
        raise HTTPException(400, f"Unsupported artifact: {artifact}")

    file_path = artifact_paths[artifact]

    if not file_path.exists():
        raise HTTPException(404, f"{artifact.upper()} artifact not found.")

    if artifact == "json":
        data = json.loads(file_path.read_text(encoding="utf-8"))
        return JSONResponse(content=data)

    return FileResponse(path=file_path, filename=file_path.name)


@router.get("/{scan_id}/list")
def list_artifacts(scan_id: str):
    info = SCANS.get(scan_id)
    if not info or "output_dir" not in info:
        raise HTTPException(404, "Scan not found.")

    repo_name = info.get("repo_name")
    output_dir = Path(info["output_dir"])

    available = available_artifacts(scan_id, output_dir, repo_name)
    return {"artifacts": available}
