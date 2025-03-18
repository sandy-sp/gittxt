# src/gittxt-ui/backend/core/scanning_service.py

import asyncio
from pathlib import Path
from typing import Dict, List, Optional
import uuid

from gittxt.repository import RepositoryHandler
from gittxt.scanner import Scanner
from gittxt.output_builder import OutputBuilder
from gittxt.utils.cleanup_utils import cleanup_temp_folder
from gittxt.logger import Logger

logger = Logger.get_logger(__name__)

# Store scanning tasks in memory
SCANS: Dict[str, dict] = {}

# Concurrency limit: only one scan at a time
MAX_CONCURRENT_SCANS = 1
SEM = asyncio.Semaphore(MAX_CONCURRENT_SCANS)

async def run_scan_task(
    scan_id: str,
    repo_url: str,
    file_types: List[str],
    output_format: str,
    progress_callback,
    include_patterns: List[str],
    exclude_patterns: List[str],
    size_limit: Optional[int],
    branch: Optional[str],
):
    async with SEM:
        SCANS[scan_id]["status"] = "running"
        try:
            # (1) Prepare repo
            repo_handler = RepositoryHandler(source=repo_url, branch=branch)
            repo_path, subdir, is_remote = repo_handler.get_local_path()
            if not repo_path:
                raise ValueError("Repository path is invalid or does not exist.")

            scan_root = Path(repo_path)
            if subdir:
                scan_root = scan_root / subdir

            # (2) Perform scanning with partial progress
            valid_files, tree_summary = await _scan_with_custom_progress(
                scan_id, scan_root, file_types, progress_callback,
                include_patterns, exclude_patterns, size_limit
            )

            # (3) If no valid files
            if not valid_files:
                SCANS[scan_id].update({
                    "status": "done",
                    "file_count": 0,
                    "message": "No valid files found."
                })
                return

            # (4) OutputBuilder
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
            logger.info(f"Scan {scan_id} completed successfully.")

        except Exception as e:
            SCANS[scan_id]["status"] = "error"
            SCANS[scan_id]["error"] = str(e)
            logger.error(f"Scan {scan_id} failed with error: {e}")

        finally:
            # (5) If remote, remove the cloned repo
            # We DO NOT remove the 'output_dir' so the user can download artifacts.
            if is_remote:
                cleanup_temp_folder(Path(repo_path))

async def _scan_with_custom_progress(
    scan_id: str,
    scan_root: Path,
    file_types: List[str],
    progress_callback,
    include_patterns: List[str],
    exclude_patterns: List[str],
    size_limit: Optional[int],
):
    """
    Example custom scanning approach that calls progress_callback after each file.
    """
    scanner = Scanner(
        root_path=scan_root,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        size_limit=size_limit,
        file_types=file_types,
        progress=False  # We'll do our own progress
    )

    all_paths = list(scan_root.rglob("*"))
    total_count = len(all_paths)
    current_count = 0

    valid_files = []

    for path in all_paths:
        current_count += 1
        if not path.is_file():
            progress_callback(scan_id, current_count, total_count, f"Skipping dir {path.name}")
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
    tree_summary = scanner._scan_directory_sync()[1]  # or your own approach
    return valid_files, tree_summary


def update_scan_progress(scan_id: str, current: int, total: int, msg: str):
    """A callback function to update SCANS[scan_id] progress info."""
    if scan_id in SCANS:
        progress = round((current / total) * 100, 2)
        SCANS[scan_id]["progress"] = progress
        SCANS[scan_id]["current_file"] = msg


def build_directory_tree(base_path: Path) -> dict:
    """
    Recursively build a nested dict describing folders and files:
    {
      "name": "root_folder",
      "type": "directory",
      "children": [
        {...}, ...
      ]
    }
    """
    if not base_path.is_dir():
        return {"name": base_path.name, "type": "file"}

    node = {"name": base_path.name, "type": "directory", "children": []}

    for child in sorted(base_path.iterdir(), key=lambda c: c.name.lower()):
        if child.is_dir():
            node["children"].append(build_directory_tree(child))
        else:
            node["children"].append({"name": child.name, "type": "file"})
    return node

def gather_file_extensions(root: Path) -> dict:
    """
    Collects file extensions (suffixes) from all files under 'root'.

    Returns a dict like:
      {
        ".py": 14,
        ".md": 6,
        ".json": 2,
        ...
      }
    representing how many times each extension appears.
    """
    ext_map = {}
    for f in root.rglob("*"):
        if f.is_file():
            suffix = f.suffix.lower()
            ext_map[suffix] = ext_map.get(suffix, 0) + 1
    return ext_map

def remove_ephemeral_outputs(path_obj: Path):
    """
    Removes ephemeral artifacts from 'path_obj' using the existing 
    cleanup_temp_folder from gittxt.utils.cleanup_utils.
    This is typically called in /scans/{scan_id}/close to free up disk space.
    """
    # Only remove if it exists
    if path_obj.exists():
        from gittxt.utils.cleanup_utils import cleanup_temp_folder
        cleanup_temp_folder(path_obj)
