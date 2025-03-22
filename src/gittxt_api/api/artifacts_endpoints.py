from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from typing import Literal
from gittxt_api.core.scanning_service import SCANS
from pathlib import Path
import json
from gittxt_api.services.artifact_service import resolve_artifact_paths, available_artifacts

router = APIRouter()

@router.get("/{scan_id}/{artifact}")
def download_artifact(scan_id: str, artifact: Literal["txt", "json", "md", "zip"]):
    """
    Download a specific artifact file by type: txt, json, md, zip.
    """
    info = SCANS.get(scan_id)
    if not info or "output_dir" not in info:
        raise HTTPException(404, "Scan not found or incomplete.")

    repo_name = info.get("repo_name")
    output_dir = Path(info["output_dir"])

    artifact_paths = resolve_artifact_paths(scan_id, output_dir, repo_name)
    file_path = artifact_paths.get(artifact)

    if not file_path or not file_path.exists():
        raise HTTPException(404, f"{artifact.upper()} artifact not found.")

    if artifact == "json":
        # Inline JSON response
        data = json.loads(file_path.read_text(encoding="utf-8"))
        return JSONResponse(content=data)

    return FileResponse(path=file_path, filename=file_path.name)


@router.get("/{scan_id}/list")
def list_artifacts(scan_id: str):
    """
    List available artifacts (formats) for a given scan.
    """
    info = SCANS.get(scan_id)
    if not info or "output_dir" not in info:
        raise HTTPException(404, "Scan not found.")

    repo_name = info.get("repo_name")
    output_dir = Path(info["output_dir"])

    available = available_artifacts(scan_id, output_dir, repo_name)
    return {"artifacts": available}
