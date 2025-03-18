# src/gittxt-ui/backend/core/scanning_service.py

import asyncio
from pathlib import Path
from typing import Dict

from gittxt.repository import RepositoryHandler
from gittxt.scanner import Scanner
from gittxt.output_builder import OutputBuilder
from gittxt.utils.cleanup_utils import cleanup_temp_folder

# We store all scanning states here. 
# Production systems might use a real DB instead.
SCANS: Dict[str, dict] = {}

async def run_scan_task(scan_id: str, repo_url: str, file_types: str, output_format: str, progress_callback):
    """
    Background task that performs the scan. Updates SCANS dict with progress.
    """
    SCANS[scan_id]["status"] = "running"
    try:
        # 1) Prepare the repository
        repo_handler = RepositoryHandler(source=repo_url)
        repo_path, subdir, is_remote = repo_handler.get_local_path()

        scan_root = Path(repo_path)
        if subdir:
            scan_root = scan_root / subdir

        # 2) Build a custom scanning approach with partial progress
        valid_files, tree_summary = await _scan_with_custom_progress(
            scan_id, scan_root, file_types, progress_callback
        )

        # 3) If no valid files found
        if not valid_files:
            SCANS[scan_id]["status"] = "done"
            SCANS[scan_id]["file_count"] = 0
            SCANS[scan_id]["message"] = "No valid files found."
            return

        # 4) Use OutputBuilder
        output_dir = Path.cwd() / f"gittxt_scan_{scan_id}_outputs"
        builder = OutputBuilder(
            repo_name=f"scan_{scan_id}",
            output_dir=output_dir,
            output_format=output_format
        )
        builder.generate_output(valid_files, scan_root)

        SCANS[scan_id].update({
            "status": "done",
            "message": "Scan complete",
            "file_count": len(valid_files),
            "tree_summary": tree_summary,
            "output_dir": str(output_dir)
        })

    except Exception as e:
        SCANS[scan_id]["status"] = "error"
        SCANS[scan_id]["error"] = str(e)
    finally:
        # Clean up remote clone if desired
        if is_remote:
            cleanup_temp_folder(Path(repo_path))

async def _scan_with_custom_progress(scan_id: str, scan_root: Path, file_types: str, progress_callback):
    """
    Example custom scanning approach that calls progress_callback after each file.
    """
    from gittxt.scanner import Scanner

    scanner = Scanner(
        root_path=scan_root,
        include_patterns=[],
        exclude_patterns=[".git", "node_modules"],
        size_limit=None,
        file_types=file_types.split(","),
        progress=False  # We'll do our own progress
    )

    all_paths = list(scan_root.rglob("*"))
    total_count = len(all_paths)
    current_count = 0

    valid_files = []

    for path in all_paths:
        current_count += 1
        if not path.is_file():
            progress_callback(scan_id, current_count, total_count, f"Skipping (not file) {path.name}")
            continue

        # filter checks
        if not scanner._passes_filters(path):
            progress_callback(scan_id, current_count, total_count, f"Excluded {path.name}")
            continue
        if not scanner._passes_filetype_filter(path):
            progress_callback(scan_id, current_count, total_count, f"Skipping type {path.name}")
            continue

        valid_files.append(path.resolve())
        progress_callback(scan_id, current_count, total_count, f"Scanned {path.name}")

        # small async sleep so the event loop can do other tasks
        await asyncio.sleep(0)

    # after done
    tree_summary = scanner._scan_directory_sync()[1]  # reuse the built-in tree or generate your own
    return valid_files, tree_summary


def update_scan_progress(scan_id: str, current: int, total: int, msg: str):
    """A callback function to update SCANS[scan_id] progress info."""
    if scan_id in SCANS:
        progress = round((current / total) * 100, 2)
        SCANS[scan_id]["progress"] = progress
        SCANS[scan_id]["current_file"] = msg
