from pathlib import Path
from typing import Dict

def resolve_artifact_paths(scan_id: str, output_dir: Path, repo_name: str) -> Dict[str, Path]:
    """
    Centralizes artifact path resolution logic.
    """
    return {
        "txt": output_dir / "text" / f"{repo_name}.txt",
        "json": output_dir / "json" / f"{repo_name}.json",
        "md": output_dir / "md" / f"{repo_name}.md",
        "zip": output_dir / "zips" / f"{repo_name}_bundle.zip",
    }

def available_artifacts(scan_id: str, output_dir: Path, repo_name: str) -> Dict[str, str]:
    """
    Returns a dictionary of available artifact URLs based on existing files.
    """
    available = {}
    paths = resolve_artifact_paths(scan_id, output_dir, repo_name)

    for fmt, path in paths.items():
        if path.exists():
            available[fmt] = f"/artifacts/{scan_id}/{fmt}"

    return available
