from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from core.scanning_service import SCANS
from pathlib import Path
import json

router = APIRouter()

@router.get("/{scan_id}/{artifact}")
def download_artifact(scan_id: str, artifact: str):
    """Unified handler for txt, json, md, zip artifacts"""
    info = SCANS.get(scan_id)
    if not info or "output_dir" not in info:
        raise HTTPException(404, "Scan not found or incomplete.")

    repo_name = info.get("repo_name")
    output_dir = Path(info["output_dir"])

    artifact_map = {
        "txt": output_dir / "text" / f"{repo_name}.txt",
        "json": output_dir / "json" / f"{repo_name}.json",
        "md": output_dir / "md" / f"{repo_name}.md",
        "zip": output_dir / "zips" / f"{repo_name}_bundle.zip",
    }

    if artifact not in artifact_map:
        raise HTTPException(400, f"Unsupported artifact: {artifact}")

    file_path = artifact_map[artifact]

    if not file_path.exists():
        raise HTTPException(404, f"{artifact.upper()} artifact not found.")

    if artifact == "json":
        data = json.loads(file_path.read_text(encoding="utf-8"))
        return JSONResponse(content=data)

    return FileResponse(path=file_path, filename=file_path.name)


@router.get("/{scan_id}/list")
def list_artifacts(scan_id: str):
    """List available artifacts for a given scan_id"""
    info = SCANS.get(scan_id)
    if not info or "output_dir" not in info:
        raise HTTPException(404, "Scan not found.")

    repo_name = info.get("repo_name")
    output_dir = Path(info["output_dir"])

    available = {}
    for fmt in ["txt", "json", "md", "zip"]:
        path = output_dir / ("zips" if fmt == "zip" else fmt) / (f"{repo_name}_bundle.zip" if fmt == "zip" else f"{repo_name}.{fmt}")
        if path.exists():
            available[fmt] = f"/artifacts/{scan_id}/{fmt}"

    return {"artifacts": available}
